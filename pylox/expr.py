from dataclasses import dataclass
from pylox.token import Token
from typing import Any


class Expr:
    def accept(self, visitor):
        pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_binary(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_unary(self)


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor):
        return visitor.visit_var_expression(self)


@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_var_assignment(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_grouping(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor):
        return visitor.visit_literal(self)


@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_logical(self)


class AstPrinter:
    def print(self, expr):
        return expr.accept(self)

    def visit_binary(self, expr: Binary):
        return f"({expr.operator.lexeme} {expr.left.accept(self)} {expr.right.accept(self)})"

    def visit_unary(self, expr: Unary):
        return f"({expr.operator.lexeme} {expr.right.accept(self)})"

    def visit_grouping(self, expr: Grouping):
        return f"(group {expr.expression.accept(self)})"

    def visit_literal(self, expr: Literal):
        return f"{expr.value}"

