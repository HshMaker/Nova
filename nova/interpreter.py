from nova.ast_nodes import *
from nova.runtime import runtime
from nova.errors import *
from nova.values.variable import *
from nova.values.array import *
from nova.values.function import *
from nova.values.object import *
from nova.values.pack import *
from nova.lexer import tokenize
from nova.parser import Parser


class Interpreter:
    def __init__(self):
        self.variables: dict[str, Variable] = {}
        self.functions: dict[str, Function] = {}

        self.sendings = set()
        self.packs = {}

        self.current_instance = None

        self.VALID_TYPES = {
            "int",
            "float",
            "string",
            "bool",
            "object",
            "any"
        }

    def execute(self, program):
        for statement in program.statements:
            self.visit(statement)

    def visit(self, node):
        method_name = (
            f"visit_{type(node).__name__}"
        )
        visitor = getattr(
            self,
            method_name
        )
        return visitor(node)

    def visit_ExpressionStatement(
        self,
        node
    ):
        return self.visit(
            node.expression
        )

    def visit_PropertyExpression(
        self,
        node: PropertyExpression
    ):
        target = self.visit(node.target)

        if (isinstance(target, PackInstance)):
            if (
                node.property_name in target.properties
            ):
                return target.properties[node.property_name].value
            method = target.pack.methods.get(node.property_name)

            if (method):
                return (target, method)

        try:
            return target.get_property(node.property_name)
        except AttributeError:
            raise RuntimeError(
                f"{type(target).__name__} does not support property access."
            )

    def visit_CallExpression(
        self,
        node: CallExpression
    ):
        arguments = [
            self.visit(arg)
            for arg in node.arguments
        ]

        callee = self.visit(node.callee)

        # 일반 함수
        if (isinstance(callee, Function)):
            return self.call_function(callee, arguments)

        if (isinstance(callee, Pack)):
            instance = PackInstance(callee, {})
            init_method = callee.special_methods.get("init")

            if (init_method):
                self.call_method(instance, init_method, arguments)
                return instance

        if (isinstance(callee, tuple) and isinstance(callee[0], PackInstance)):
            return self.call_method(callee[0], callee[1], arguments)

        for i, arg in enumerate(arguments):

            if isinstance(arg, PackInstance):

                arguments[i] = self.call_appear(arg)

        if callable(callee):
            if (
                isinstance(callee.__self__, Array)
                and callee.__name__ == "push"
            ):
                array = callee.__self__
                value = arguments[0]
                value_type = self.infer_type(value)
                if array.element_type == "any":
                    array.element_type = value_type
                if (array.element_type != value_type):
                    raise RuntimeError(
                        f"Expected {array.element_type}, got {value_type}"
                    )
                return callee(value)
            return callee(*arguments)
        raise RuntimeError(
            "Object is not callable"
        )

    def call_function(
        self,
        func: Function,
        arguments
    ):
        variadic = None
        for param in func.parameters:
            if (param.is_variadic):
                variadic = param
                break
        if (variadic is None):
            if (len(arguments) != len(func.parameters)):

                raise RuntimeError(
                    f"Expected {len(func.parameters)} arguments, got {len(arguments)}"
                )
        else:
            required_count = len(func.parameters) - 1
            if (len(arguments) < required_count):
                raise RuntimeError(
                    f"Expected {len(func.parameters)} arguments, got {len(arguments)}"
                )

        old_variables = self.variables.copy()
        self.variables = func.closure.copy()

        arg_index = 0

        for param in func.parameters:

            if (param.is_variadic):
                if (param != func.parameters[-1]):
                    raise SyntaxError(
                        "Variadic parameter must be the last parameter."
                    )

                remaining = arguments[arg_index:]
                if (len(remaining) == 0):
                    inferred = "any"
                else:
                    inferred = self.infer_type(remaining[0])
                if (
                    param.data_type
                    and param.data_type != "any"
                    and param.data_type != inferred
                ):
                    for value in remaining:
                        actual = self.infer_type(value)
                        if actual != param.data_type:
                            raise RuntimeError(
                                f"Expected "
                                f"{param.data_type}, "
                                f"got "
                                f"{actual}"
                            )

                if (len(remaining) == 0):
                    variadic_array = Array([], "any")
                else:
                    element_type = self.infer_type(remaining[0])
                    if (any(element_type != self.infer_type(item) for item in remaining)):
                        raise RuntimeError(
                            "Mixed array types are not allowed.")

                    variadic_array = Array(
                        remaining,
                        element_type
                    )

                self.variables[param.name] = Variable(
                    type_name=f"array<{variadic_array.element_type}>",
                    value=variadic_array
                )
                break

            value = arguments[arg_index]

            inferred = self.infer_type(value)

            if (
                param.data_type
                and param.data_type != "any"
                and param.data_type != inferred
            ):
                raise RuntimeError(
                    f"Expected {param.data_type}, "
                    f"got {inferred}"
                )

            self.variables[param.name] = Variable(
                type_name=(
                    param.data_type
                    if (
                        param.data_type
                        and param.data_type != "any"
                    )
                    else inferred
                ),
                value=value
            )
            arg_index += 1

        try:
            for stmt in func.body:
                self.visit(stmt)
        except ReturnException as ret:

            actual_type = self.infer_type(ret.value)
            if (
                func.return_type
                and func.return_type != "any"
                and func.return_type != actual_type
            ):
                raise RuntimeError(
                    f"Function '{func.name}' must return {func.return_type}, got {actual_type}"
                )
            return ret.value

        finally:
            self.variables = old_variables

    # 연산
    def visit_BinaryExpression(
        self,
        node
    ):
        left = self.visit(
            node.left
        )

        right = self.visit(
            node.right
        )
        if node.operator == "AND":
            return left and right
        elif node.operator == "OR":
            return left or right
        elif node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            if (type(left) == float or type(right) == float):
                return left / right
            return left // right
        elif node.operator == "%":
            return left % right
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right
        elif node.operator == ">":
            return left > right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "<=":
            return left <= right

        raise RuntimeError(
            f"Unknown operator: {node.operator}"
        )

    def visit_UnaryExpression(
        self,
        node
    ):
        value = self.visit(node.operand)
        if (node.operator == "NOT"):
            return not value

    # 변수
    def visit_VariableDeclaration(
        self,
        node: VariableDeclaration
    ):
        value = self.visit(node.value)

        # inferred = self.infer_type(value)
        # declared = (node.data_type or inferred)

        # if (isinstance(value, Array) and len(value.elements) == 0):
        #     if node.data_type is None:

        #         raise RuntimeError(
        #             "Cannot infer type "
        #             "of empty array."
        #         )
        # if (isinstance(value, Array) and node.data_type):
        #     if (value.element_type != "any"):
        #         if (node.data_type == "array"):
        #             raise RuntimeError(
        #                 "Empty arrays require an explicit element type.")
        #     else:
        #         self.check_array_type(node.data_type)
        #         if (node.data_type.startswith("array<")):
        #             if (value.element_type == "any"):
        #                 value.element_type = node.data_type[6:-1]
        #                 inferred = node.data_type

        # if (declared != inferred):
        #     raise RuntimeError(
        #         f"Expected {declared}, "
        #         f"got {inferred}"
        #     )

        self.variables[node.name] = self.create_variable(
            node.data_type, value
        )
        return value

    def visit_Identifier(
        self,
        node
    ):
        runtime_obj = runtime.get(node.name)
        if (runtime_obj):
            return runtime_obj

        func = self.functions.get(node.name)

        if (func):
            return func

        pack = self.packs.get(node.name)
        if (pack):
            return pack

        if node.name not in self.variables:
            raise RuntimeError(
                f"Variable '{node.name}' is not defined"
            )

        return self.variables[node.name].value

    def visit_Assignment(
        self,
        node
    ):
        value = self.visit(node.value)
        target = node.target

        if (isinstance(target, Identifier)):

            if target.name not in self.variables:
                raise RuntimeError(
                    f"Variable '{target.name}' is not defined."
                )

            variables = self.variables[target.name]

            actual = self.infer_type(value)

            if (variables.type_name != actual):
                raise RuntimeError(
                    f"{target.name} is {variables.type_name}, not {actual}"
                )

            variables.value = value

            return value
        elif (isinstance(target, IndexExpression)):
            array = self.visit(
                target.target
            )

            index = self.visit(
                target.index
            )

            given_type = self.infer_type(value)
            if (array.element_type != given_type):
                raise RuntimeError(
                    f"Expected {array.element_type}, got {given_type}"
                )
            array.elements[index] = value

            return value
        elif (isinstance(target, PropertyExpression)):
            obj = self.visit(target.target)
            if (not isinstance(obj, Object)):
                raise RuntimeError("Property assignment requires an object.")
            obj.properties[target.property_name] = value
            return value
        elif (isinstance(target, SelfProperty)):
            if (self.current_instance is None):
                raise RuntimeError("Cannot assign # property ouside pack.")

            existing = self.current_instance.properties.get(target.name)

            if (existing is None):
                if (target.data_type is None):
                    target.data_type = self.infer_type(value)
                variable = self.create_variable(target.data_type, value)

                self.current_instance.properties[target.name] = variable
                return value

            actual = self.infer_type(value)

            if (existing.type_name != actual):
                raise RuntimeError(
                    f"Expected {existing.type_name} got {actual}")

            existing.value = value

            return value

    def create_variable(self, data_type, value):
        inferred = self.infer_type(value)
        declared = (data_type or inferred)

        if (isinstance(value, Array) and len(value.elements) == 0):
            if data_type is None:

                raise RuntimeError(
                    "Cannot infer type "
                    "of empty array."
                )
        if (isinstance(value, Array) and data_type):
            if (value.element_type != "any"):
                if (data_type == "array"):
                    raise RuntimeError(
                        "Empty arrays require an explicit element type.")
            else:
                self.check_array_type(data_type)
                if (data_type.startswith("array<")):
                    if (value.element_type == "any"):
                        value.element_type = data_type[6:-1]
                        inferred = data_type

        if (declared != inferred):
            raise RuntimeError(
                f"Expected {declared}, "
                f"got {inferred}"
            )

        return Variable(
            declared,
            value
        )

    def check_array_type(self, type_name):

        while type_name.startswith("array<") and type_name.endswith(">"):
            type_name = type_name[6:-1]

        if type_name not in self.VALID_TYPES:
            raise ValueError(f"Unknown Type '{type_name}'")

        return True

    def infer_type(self, value):
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, Object):
            return "object"
        elif isinstance(value, Array):
            if (len(value.elements) == 0):
                return "array<any>"

            element_type = type(value.elements[0])
            if (all(element_type == type(item) for item in value.elements)):
                return f"array<{self.infer_type(value.elements[0])}>"

            raise RuntimeError(
                "Type Mixed Error"
            )
        elif isinstance(value, PackInstance):
            return value.pack.name

        return "unknown"

    # if 실행

    def visit_IfStatement(
        self,
        node
    ):
        for branch in node.branches:
            if branch.condition is None:
                for stmt in branch.body:
                    self.visit(stmt)
                return
            elif self.visit(branch.condition):
                for stmt in branch.body:
                    self.visit(stmt)
                return

    # 반복문 실행
    def visit_RepeatStatement(
        self,
        node
    ):
        while self.visit(node.condition):
            try:
                for stmt in node.body:
                    self.visit(stmt)
            except NextException:
                continue

            except OutException:
                break

    def visit_NextStatement(
        self,
        node
    ):
        raise NextException()

    def visit_OutStatement(
        self,
        node
    ):
        raise OutException()

    # 함수
    def visit_FunctionDeclaration(
        self,
        node
    ):
        if (node.name in self.functions):
            raise RuntimeError(
                f"function {node.name} is already exist."
            )
        self.functions[node.name] = self.build_function(node)

    def build_function(self, node):
        return Function(
            node.name,
            node.parameters,
            node.return_type,
            node.body,
            self.variables.copy()
        )

    def visit_ReturnStatement(
        self,
        node
    ):
        value = self.visit(node.value)

        raise ReturnException(value)

    # 배열

    def visit_IndexExpression(
        self,
        node
    ):
        target = self.visit(node.target)
        index = self.visit(node.index)

        return target.elements[index]

    # take at
    def visit_TakeStatement(
        self,
        node
    ):
        with open(node.path, "r", encoding="utf-8") as f:
            source = f.read()

            tokens = tokenize(source)

            ast = Parser(tokens).parse()
            module_interpreter = Interpreter()
            module_interpreter.execute(ast)

            exports = {}

            for name in module_interpreter.sendings:
                if (name in module_interpreter.functions):
                    exports[name] = module_interpreter.functions[name]
                elif (name in module_interpreter.packs):
                    exports[name] = module_interpreter.packs[name]
                elif (name in module_interpreter.variables):
                    raise RuntimeError("Variable cannot be sent by send.")
                else:
                    raise RuntimeError(
                        f"'{name}' was sent but does not exist.")

            export = exports.get(node.name)

            if (export is None):
                raise RuntimeError(f"'{node.name}' is not exported.")

            if (isinstance(export, Pack)):
                self.packs[node.name] = export
            elif (isinstance(export, Function)):
                self.functions[node.name] = export

    def visit_SendStatement(
        self,
        node
    ):
        # if (node.name in self.functions):
        #     self.sendings[node.name] = self.functions[node.name]
        #     return
        # raise RuntimeError(f"'{node.name}' cannot be sent")

        self.sendings.add(node.name)

    # pack
    def visit_PackDeclaration(
        self,
        node
    ):

        methods = {
            name: self.build_function(method)
            for name, method in node.methods.items()
        }
        special_methods = {
            name: self.build_function(method)
            for name, method in node.special_methods.items()
        }
        self.packs[node.name] = Pack(
            node.name,
            methods,
            special_methods
        )

        self.VALID_TYPES.add(node.name)

    def visit_SelfProperty(
        self,
        node
    ):
        if (
            self.current_instance
            is None
        ):
            raise RuntimeError(
                "Cannot use # outside pack."
            )

        if (node.name == "this"):

            return self.current_instance

        variable = self.current_instance.properties.get(node.name)
        if (variable):
            return variable.value

        method = self.current_instance.pack.methods.get(node.name)
        if (method):
            return (self.current_instance, method)

        special_method = self.current_instance.pack.special_methods.get(
            node.name)
        if (special_method):
            return (self.current_instance, special_method)

        raise RuntimeError(f"Field or Method '{node.name}' is not defined.")

    def call_method(
        self,
        instance,
        method,
        arguments
    ):

        old_instance = (
            self.current_instance
        )

        self.current_instance = (
            instance
        )

        try:
            return self.call_function(
                method,
                arguments
            )

        finally:
            self.current_instance = (
                old_instance
            )

    def call_appear(
        self,
        instance: PackInstance
    ):

        appear = instance.pack.special_methods.get("appear")

        if appear is None:
            return (
                f"<{instance.pack.name}>"
            )

        return self.call_method(
            instance,
            appear,
            []
        )

    # 클래스 벗겨내기

    def visit_StringLiteral(
        self,
        node
    ):
        return node.value

    def visit_NumberLiteral(
        self,
        node
    ):
        return node.value

    def visit_BooleanLiteral(
        self,
        node
    ):
        return node.value

    def visit_ArrayLiteral(
        self,
        node: ArrayLiteral
    ):

        elements = [
            self.visit(element)
            for element in node.elements
        ]
        if (len(elements) == 0):
            return Array([], "any")

        element_type = self.infer_type(elements[0])
        if (any(element_type != self.infer_type(item) for item in elements)):
            raise RuntimeError("Mixed array types are not allowed.")

        return Array(
            elements,
            element_type
        )

    def visit_ObjectLiteral(
        self,
        node
    ):
        return Object(
            {
                key:
                self.visit(value)

                for key, value
                in node.properties.items()
            }
        )
