from dataclasses import dataclass, field
from typing import Any
from pylox.token import Token
from pylox.runtime_error import RuntimeError as LoxRuntimeError

@dataclass
class Environment:
    enclosing: 'Environment' = None
    values: dict = field(default_factory=dict)

    def get(self, name: Token):
        try:
            return self.values[name.lexeme]
        except KeyError: 
            if self.enclosing:
                return self.enclosing.get(name)
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise LoxRuntimeError(name, 
        f"Undefined variable: {name.lexeme}.")


    def define(self, name: str, value: Any):
        self.values[name] = value
