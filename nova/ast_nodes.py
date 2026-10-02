from dataclasses import dataclass


@dataclass
class Program:
    statements: list

# 함수


@dataclass
class ExpressionStatement:
    expression: object


@dataclass
class NativeCallExpression:
    path: list[str]
    arguments: list


@dataclass
class FunctionCallExpression:
    name: str
    arguments: list


@dataclass
class CallExpression:
    callee: object
    arguments: list

# 자료형


@dataclass
class StringLiteral:
    value: str


@dataclass
class NumberLiteral:
    value: int | float


@dataclass
class BooleanLiteral:
    value: bool


@dataclass
class ArrayLiteral:
    elements: list


@dataclass
class IndexExpression:
    target: object
    index: object


@dataclass
class ObjectLiteral:
    properties: dict


@dataclass
class PropertyExpression:
    target: object
    property_name: str

# 연산


@dataclass
class BinaryExpression:
    left: object
    operator: str
    right: object


@dataclass
class UnaryExpression:
    operator: str
    operand: object

# 변수


@dataclass
class Identifier:
    name: str


@dataclass
class VariableDeclaration:
    name: str
    data_type: str | None
    value: object


@dataclass
class Assignment:
    target: object
    value: object


# if문


@dataclass
class IfBranch:
    condition: object | None
    body: list


@dataclass
class IfStatement:
    branches: list[IfBranch]


# 반복문


@dataclass
class RepeatStatement:
    condition: object
    body: list


@dataclass
class NextStatement:
    pass


@dataclass
class OutStatement:
    pass


# 함수


@dataclass
class Parameter:
    name: str
    data_type: str | None
    is_variadic: bool = False


@dataclass
class ReturnStatement:
    value: object


@dataclass
class FunctionDeclaration:
    name: str
    parameters: list[Parameter]
    return_type: str | None
    body: list

# take at


@dataclass
class TakeStatement:
    name: str
    path: str


@dataclass
class SendStatement:
    name: str


# pack

@dataclass
class PackDeclaration:
    name: str
    methods: list
    special_methods: list


@dataclass
class SelfProperty:
    name: str
    data_type: str | None
