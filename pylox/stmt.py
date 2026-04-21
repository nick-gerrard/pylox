from dataclasses import dataclass
from pylox.expr import Expr
from pylox.token import Token
from typing import Any

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
    initializer: Expr

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)
