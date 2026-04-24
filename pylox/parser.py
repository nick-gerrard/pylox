from dataclasses import dataclass
from pylox.token import Token, TokenType
from pylox.expr import (
    Expr,
    Literal,
    Unary,
    Binary,
    Grouping,
    Variable,
    Assign,
    Logical,
    Call,
)
from pylox.stmt import Stmt, Print, Expression, Var, Block, If, While, Function
from pylox.error_reporter import token_error
from typing import List


@dataclass
class Parser:
    tokens: List[Token]
    current: int = 0

    def parse(self):
        statements = []
        while not self._is_at_end():
            statements.append(self.declaration())
        return statements

    def _is_at_end(self):
        if self._peek().token_type != TokenType.EOF:
            return False
        return True

    def _match(self, *token_types):
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type):
        if self._is_at_end():
            return False
        if self._peek().token_type == token_type:
            return True
        return False

    def _advance(self):
        token = self.tokens[self.current]
        self.current += 1
        return token

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    class ParseError(Exception):
        def __init__(self, token, message):
            self.token = token
            self.message = message
            super().__init__(message)

    def _error(self, token, message):
        token_error(token, message)
        return self.ParseError(token, message)

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            match self._peek().token_type:
                case (
                    TokenType.CLASS
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.FOR
                    | TokenType.IF
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ):
                    return

            self._advance()

    def _consume(self, token_type, message=None):
        if self._peek().token_type == token_type:
            return self._advance()
        else:
            raise self._error(self._peek(), message)

    def _print_statement(self):
        value = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _expression_statement(self):
        expr = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)

    def _function(self, kind: str):
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            parameters.append(self._consume(TokenType.IDENTIFIER))
            while self._match(TokenType.COMMA):
                if len(parameters) > 255:
                    self._error(self._peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")
        body = self._block()
        return Function(name, parameters, body)

    def _block(self):
        statements = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self.declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr | None = None

        if self._match(TokenType.EQUAL):
            initializer = self.expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after var declaration.")
        return Var(name, initializer)

    def _while_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body: Stmt = self.statement()
        return While(condition=condition, body=body)

    def _if_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        then_branch: Stmt = self.statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def primary(self):
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def finish_call(self, callee):
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self._match(TokenType.COMMA):
                arguments.append(self.expression())
                if len(arguments) > 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")

        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren=paren, arguments=arguments)

    def call(self):
        expr: Expr = self.primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def unary(self):
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def factor(self):
        expr = self.unary()
        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def assignment(self):
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            self._error(equals, "Invalid assignment target.")
        return expr

    def _or(self):
        expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)
        return expr

    def _and(self):
        expr = self.equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def expression(self):
        return self.assignment()

    def statement(self):
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())

        return self._expression_statement()

    def _for_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self.expression()
        self._consume(TokenType.SEMICOLON)

        increment: Expr | None = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body: Stmt = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)
        body = While(condition=condition, body=body)

        if initializer is not None:
            body = Block([initializer, body])
        return body

    def declaration(self):
        try:
            if self._match(TokenType.FUN):
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self.statement()
        except self.ParseError:
            self._synchronize()
            return None
