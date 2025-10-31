from __future__ import annotations
from dataclasses import dataclass, field
from math import dist
import time
from lox.runtime import NativeFunction

@dataclass
class Env[T]:
    values: dict[str, T] = field(default_factory=dict)
    enclosing: Env | None = None

    @classmethod
    def globals(cls) -> "Env":
        return cls({"clock": NativeFunction(time.time, arity=0)})

    def __setitem__(self, name: str, value: T) -> None:
        self.values[name] = value

    def __getitem__(self, name: str) -> T:
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing[name]
        raise NameError(name)

    def assign(self, name: str, value: T):
        if name in self.values:
            self.values[name] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)  
        else:
            raise NameError(name)

    def push(self) -> Env:
        return Env(enclosing=self)
    
    def get_at(self, depth: int, name: str) -> T: 
        while depth > 0:
            self = self.enclosing
            depth -= 1
        if name in self.values:
            return self.values[name]
        raise NameError(name)

    def assign_at(self, depth: int, name: str, value: T) -> None:
        while depth > 0:
            self = self.enclosing
            depth -= 1
        
        if name not in self.values:
            raise NameError(name)
        self.values[name] = value
