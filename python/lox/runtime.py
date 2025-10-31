from __future__ import annotations
import abc
from dataclasses import dataclass, field
from typing import Callable
from lox.ast import Function
from lox import env, interpreter
from lox.errors import LoxRuntimeError
from lox.tokens import Token

type Value = interpreter.Value
type Env = env.Env[Value]


class LoxCallable(abc.ABC):
    arity: int
    
    @abc.abstractmethod
    def call(self,
             env: Env,
             arguments: list[Value]) -> Value:
        ...


@dataclass(eq=False)
class NativeFunction(LoxCallable):
    function: Callable[..., Value]
    arity: int

    def call(self,
             env: Env,
             arguments: list[Value]) -> Value:
        return self.function(*arguments)

    def __str__(self) -> str:
        return "<native fn>"
    

@dataclass(eq=False)
class LoxFunction(LoxCallable):
    declaration: Function
    closure: Env
    is_initializer: bool = False

    @property
    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self,
             env: Env,
             arguments: list[Value]) -> Value:
        env = self.closure.push()
        for param, arg in zip(self.declaration.params, arguments):
            env[param.lexeme] = arg

        try:
            for stmt in self.declaration.body:
                interpreter.exec(stmt, env)
        except LoxReturn as result:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return result.value
        except RecursionError:
            msg = "Stack overflow."
            raise LoxRuntimeError(msg, self.declaration.name)
        if self.is_initializer:
            return self.closure.get_at(0, "this")
    
    def bind(self, instance: LoxInstance) -> LoxFunction:
        env = self.closure.push()
        env["this"] = instance
        return LoxFunction(self.declaration, env, self.is_initializer)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
   
class LoxReturn(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


@dataclass(eq=False)
class LoxClass(LoxCallable):
    name: str
    superclass: LoxClass | None = None
    methods: dict[str, LoxFunction] = field(default_factory=dict)

    @property
    def arity(self) -> int:
        init = self.find_method("init")
        if init is None:
            return 0
        return init.arity

    def __str__(self) -> str:
        return self.name
    
    def call(self, env: Env, arguments: list[Value]) -> LoxInstance:
        instance = LoxInstance(self)
        init = self.find_method("init")
        if init is not None:
            init.bind(instance).call(env, arguments)
        return instance
        
    def find_method(self, name: str) -> LoxFunction | None:
        if method := self.methods.get(name):
            return method
        if self.superclass is not None:
            return self.superclass.find_method(name)

@dataclass(eq=False)
class LoxInstance:
    klass: LoxClass
    fields: dict[str, Value] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.klass.name} instance"
    
    def get(self, name: Token) -> Value:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise LoxRuntimeError(f"Undefined property '{name.lexeme}'.", name)

    def set(self, name: Token, value: Value) -> None:
        self.fields[name.lexeme] = value
