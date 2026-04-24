from abc import ABC, abstractmethod


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int: ...

    @abstractmethod
    def call(self, interpreter, arguments: list): ...
