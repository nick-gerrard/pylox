from dataclasses import dataclass
from pylox.expr import Expr
from pylox.token import Token
from typing import List


class Stmt:
    def accept(self, visitor):
        pass


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_expression(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_print(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)
