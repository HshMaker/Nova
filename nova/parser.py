from nova.ast_nodes import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def consume(self):
        token = self.current()
        if token is None:
            raise SyntaxError(
                "Unexpected end of file"
            )

        self.pos += 1
        return token

    def expect(self, token_type):
        token = self.current()

        if token is None:
            raise SyntaxError(
                "Unexpected end of file"
            )

        if token[0] != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {token[0]} and it's {token[1]}"
            )

        self.pos += 1
        return token

    def parse(self):
        statements = []
        while self.current():
            statements.append(
                self.parse_statement()
            )
        return Program(statements)

    def parse_statement(self):
        current = self.current()
        if current[0] == "VAR":  # 변수의 경우
            return self.parse_var_decl()
        elif current[0] == "IF":  # if문의 경우
            return self.parse_if()
        elif current[0] == "REPEAT":  # repeat문의 경우
            return self.parse_repeat()
        elif current[0] == "NEXT":  # next의 경우
            self.consume()
            return NextStatement()
        elif current[0] == "OUT":  # out의 경우
            self.consume()
            return OutStatement()
        elif current[0] == "FUN":  # 함수 선언의 경우
            return self.parse_function()
        elif current[0] == "RETURN":  # return의 경우
            return self.parse_return()
        elif current[0] == "TAKE":  # take의 경우
            return self.parse_take()
        elif current[0] == "SEND":  # send의 경우
            return self.parse_send()
        elif current[0] == "PACK":
            return self.parse_pack()
        # 그 외의 경우
        expr = self.parse_expression()
        if not isinstance(expr, (CallExpression, Assignment)):
            raise SyntaxError("Only function calls can be used as statements")

        return ExpressionStatement(expr)

    def parse_expression(self):
        return self.parse_assignment()

    def parse_primary(self):
        current = self.current()

        if current[0] == "LPAREN":
            self.consume()
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr

        elif current[0] == "STRING":
            value = self.consume()[1]
            return StringLiteral(value[1:-1])

        elif current[0] == "NUMBER":
            value = self.consume()[1]
            if "." in value:
                return NumberLiteral(float(value))

            return NumberLiteral(int(value))

        elif current[0] == "LBRACKET":
            return self.parse_array()

        elif current[0] == "BOOLEAN":
            value = self.consume()[1]
            return BooleanLiteral(value == "true")

        elif current[0] == "LBRACE":
            return self.parse_object()

        elif current[0] == "HASH":

            self.consume()
            name = self.expect("IDENT")[1]

            data_type = None

            if (
                self.current()
                and self.current()[0] == "COLON"
            ):
                self.consume()

                data_type = self.parse_type()

            expr = SelfProperty(name, data_type)

            while self.current():
                if (self.current()[0] == "DOT"):
                    self.consume()
                    property_name = self.expect("IDENT")[1]
                    expr = PropertyExpression(expr, property_name)

                    continue
                if (self.current()[0] == "LPAREN"):
                    self.consume()
                    arguments = []
                    while (self.current() and self.current()[0] != "RPAREN"):
                        arguments.append(self.parse_expression())

                        if (self.current() and self.current()[0] == "COMMA"):
                            self.consume()

                    self.expect("RPAREN")

                    expr = CallExpression(expr, arguments)
                    continue
                break

            return expr

        elif current[0] == "IDENT":
            expr = Identifier(self.consume()[1])
            while (self.current()):
                # .name
                if (self.current()[0] == "DOT"):
                    self.consume()
                    property_name = self.expect("IDENT")[1]
                    expr = PropertyExpression(expr, property_name)
                    continue
                # (...)
                if (self.current()[0] == "LPAREN"):
                    self.consume()
                    arguments = []

                    while (
                        self.current()
                        and self.current()[0] != "RPAREN"
                    ):
                        arguments.append(self.parse_expression())

                        if (self.current() and self.current()[0] == "COMMA"):
                            self.consume()

                    self.expect("RPAREN")

                    expr = CallExpression(
                        expr,
                        arguments
                    )
                    continue
                # [...]
                if (self.current()[0] == "LBRACKET"):
                    expr = self.parse_index(expr)
                    continue
                break

            return expr

        raise SyntaxError(
            f"Unexpected token: {self.current()}"
        )

    # 연산
    def parse_or(self):
        left = self.parse_and()

        while (
            self.current()
            and self.current()[0] == "OR"
        ):
            op = self.consume()[0]

            right = self.parse_and()

            left = BinaryExpression(
                left,
                op,
                right
            )

        return left

    def parse_and(self):
        left = self.parse_comparison()

        while (
            self.current()
            and self.current()[0] == "AND"
        ):
            op = self.consume()[0]

            right = self.parse_comparison()

            left = BinaryExpression(
                left,
                op,
                right
            )

        return left

    def parse_comparison(self):
        left = self.parse_term()

        while (
            self.current()
            and self.current()[0] in (
                "EQEQ",
                "NOTEQ",
                "GT",
                "LT",
                "GTE",
                "LTE"
            )
        ):
            op = self.consume()[1]
            right = self.parse_term()
            left = BinaryExpression(
                left,
                op,
                right
            )

        return left

    def parse_term(self):
        left = self.parse_factor()

        while (
            self.current()
            and self.current()[0] in (
                "PLUS",
                "MINUS"
            )
        ):
            op = self.consume()[1]

            right = self.parse_factor()

            left = BinaryExpression(
                left,
                op,
                right
            )

        return left

    def parse_factor(self):
        left = self.parse_unary()

        while (
            self.current()
            and self.current()[0] in (
                "STAR",
                "SLASH",
                "MOD"
            )
        ):
            op = self.consume()[1]

            right = self.parse_primary()

            left = BinaryExpression(
                left,
                op,
                right
            )

        return left

    def parse_unary(self):
        if (
            self.current()
            and self.current()[0] == "NOT"
        ):
            self.consume()

            return UnaryExpression(
                "NOT",
                self.parse_unary()
            )

        return self.parse_primary()

    # 변수

    def parse_var_decl(self):
        self.expect("VAR")

        name = self.expect("IDENT")[1]

        data_type = None

        if (
            self.current()
            and self.current()[0] == "COLON"
        ):
            self.consume()
            data_type = self.parse_type()

        self.expect("ASSIGN")

        value = self.parse_expression()

        return VariableDeclaration(
            name,
            data_type,
            value
        )

    def parse_type(self):
        type = self.expect("IDENT")[1]

        if (self.current() and self.current()[0] == "LT"):
            self.consume()

            inner = self.parse_type()

            self.expect("GT")
            return f"{type}<{inner}>"

        return type

    def parse_assignment(self):
        left = self.parse_or()

        if (
            self.current()
            and self.current()[0] == "ASSIGN"
        ):
            self.consume()

            value = self.parse_expression()

            return Assignment(
                left,
                value
            )

        return left

    # if문
    def parse_if(self):
        branches = []

        self.expect("IF")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        self.expect("THEN")

        body = []

        while (self.current()
               and self.current()[0] not in ("OTHER", "END")
               ):
            body.append(
                self.parse_statement()
            )

        branches.append(
            IfBranch(condition, body)
        )
        while (
            self.current()
            and self.current()[0] == "OTHER"
        ):
            self.consume()
            if (
                self.current()
                and self.current()[0] == "IF"
            ):
                # other if문
                self.consume()
                condition = self.parse_expression()

                self.expect("THEN")

                body = []

                while (
                    self.current()
                    and self.current()[0]
                    not in ("OTHER", "END")
                ):
                    body.append(self.parse_statement())

                branches.append(
                    IfBranch(condition, body)
                )
            else:
                # other 문
                body = []
                self.expect("THEN")
                while (
                    self.current()
                    and self.current()[0] != "END"
                ):
                    body.append(self.parse_statement())

                branches.append(
                    IfBranch(None, body)
                )

                break

        self.expect("END")

        return IfStatement(branches)

    # 반복문
    def parse_repeat(self):
        self.expect("REPEAT")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        self.expect("THEN")

        body = []

        while (
            self.current()
            and self.current()[0] != "END"
        ):
            body.append(
                self.parse_statement()
            )

        self.expect("END")

        return RepeatStatement(
            condition,
            body
        )

    # 함수
    def parse_function(self):
        self.expect("FUN")

        name = self.expect("IDENT")[1]

        self.expect("LPAREN")

        parameters = []

        while (
            self.current()
            and self.current()[0] != "RPAREN"
        ):
            is_variadic = False
            if (
                self.current()
                and self.current()[0] == "ELLIPSIS"
            ):
                self.consume()
                is_variadic = True
            param_name = self.expect("IDENT")[1]
            param_type = None

            if (
                self.current()
                and self.current()[0] == "COLON"
            ):
                self.consume()

                param_type = self.parse_type()
                # if (is_variadic):
                #     param_type = f"array<{param_type}>"

            parameters.append(
                Parameter(
                    param_name,
                    param_type,
                    is_variadic
                )
            )
            if (
                self.current()
                and self.current()[0] == "COMMA"
            ):
                self.consume()

        self.expect("RPAREN")

        return_type = None
        if (
            self.current()
            and self.current()[0] == "COLON"
        ):
            self.consume()
            return_type = self.parse_type()

        self.expect("THEN")

        body = []

        while (
            self.current()
            and self.current()[0] != "END"
        ):
            body.append(self.parse_statement())

        self.expect("END")

        return FunctionDeclaration(
            name,
            parameters,
            return_type,
            body
        )

    def parse_return(self):
        self.expect("RETURN")

        value = self.parse_expression()

        return ReturnStatement(value)

    # 배열
    def parse_array(self):
        self.expect("LBRACKET")

        elements = []

        while (
            self.current()
            and self.current()[0] != "RBRACKET"
        ):
            elements.append(
                self.parse_expression()
            )

            if (
                self.current()
                and self.current()[0] == "COMMA"
            ):
                self.consume()

        self.expect("RBRACKET")

        return ArrayLiteral(
            elements
        )

    def parse_index(self, target):
        self.expect("LBRACKET")
        index = self.parse_expression()
        self.expect("RBRACKET")

        return IndexExpression(
            target,
            index
        )

    # take at
    def parse_take(self):
        self.expect("TAKE")

        name = self.expect("IDENT")[1]

        self.expect("AT")

        path = self.expect("STRING")[1][1:-1]

        return TakeStatement(name, path)

    def parse_send(self):
        self.expect("SEND")

        name = self.expect("IDENT")[1]

        return SendStatement(name)

    # object
    def parse_object(self):
        self.expect("LBRACE")
        properties = {}

        while (self.current() and self.current()[0] != "RBRACE"):
            name = self.expect("IDENT")[1]

            self.expect("COLON")

            value = self.parse_expression()

            properties[name] = value

            if (
                self.current()
                and self.current()[0] == "COMMA"
            ):
                self.consume()
        self.expect("RBRACE")

        return ObjectLiteral(
            properties
        )

    # pack
    def parse_pack(self):
        self.expect("PACK")
        name = self.expect("IDENT")[1]

        self.expect("THEN")

        methods = {}
        special_methods = {}

        while (
            self.current()
            and self.current()[0] != "END"
        ):
            current = self.current()

            if (current[0] == "HASH"):
                method = self.parse_special_method()

                special_methods[method.name] = method
                continue
            if (current[0] == "FUN"):
                method = self.parse_function()

                methods[method.name] = method
                continue

            raise SyntaxError(f"Unexpected token {current}")
        self.expect("END")

        return PackDeclaration(
            name,
            methods,
            special_methods
        )

    def parse_special_method(self):
        self.expect("HASH")
        name = self.expect("IDENT")[1]

        self.expect("LPAREN")
        parameters = []

        while (
            self.current()
            and self.current()[0] != "RPAREN"
        ):
            is_variadic = False
            if (
                self.current()
                and self.current()[0] == "ELLIPSIS"
            ):
                self.consume()
                is_variadic = True
            param_name = self.expect("IDENT")[1]

            param_type = None

            if (
                self.current()
                and self.current()[0] == "COLON"
            ):
                self.consume()
                param_type = self.parse_type()

            parameters.append(
                Parameter(
                    param_name,
                    param_type,
                    is_variadic
                )
            )

            if (
                self.current()
                and self.current()[0] == "COMMA"
            ):
                self.consume()

        self.expect("RPAREN")
        return_type = None
        if (
            self.current()
            and self.current()[0] == "COLON"
        ):
            self.consume()
            return_type = self.parse_type()

        self.expect("THEN")

        body = []
        while (
            self.current()
            and self.current()[0] != "END"
        ):
            body.append(self.parse_statement())

        self.expect("END")

        return FunctionDeclaration(
            name,
            parameters,
            return_type,
            body
        )
