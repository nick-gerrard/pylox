from dataclasses import dataclass
from typing import Any
from pylox.lox_callable import LoxCallable
from pylox.stmt import Function
from pylox.environment import Environment


@dataclass
class LoxFunction(LoxCallable):
    declaration: Function

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments: list[Any]):
        environment: Environment = Environment(interpreter.globals)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        interpreter._execute_block(self.declaration.body, environment)
        return None

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
