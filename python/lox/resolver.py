# lox/env.py
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Literal as Enum
from functools import singledispatch

from lox.ast import *
from lox import env
from lox.tokens import Token
from lox.errors import LoxStaticError, LoxSyntaxError

type FunctionContext = Enum["FUNCTION", "METHOD", "INITIALIZER", None]
type ClassContext = Enum["CLASS", "SUBCLASS", None]
type Resolution = Enum["DECLARED", "DEFINED"]

def resolve(program: Program) -> Program:
    env = Env()
    program = deepcopy(program)
    resolve_node(program, env)
    if env.errors:
        raise LoxStaticError(env.errors)
    return program

@dataclass
class Env(env.Env[Resolution]):
    function_context : FunctionContext = None
    class_context: ClassContext = None
    errors: list[Exception] = field(default_factory=list)

    def declare(self, name: Token) -> None:
        if not self.enclosing:
            return
        if name.lexeme in self.values:
            msg = "Already a variable with this name in this scope."
            self.error(name, msg)
        self[name.lexeme] = "DECLARED"

    def define(self, name: Token) -> None:
        if not self.enclosing:
            return
        self[name.lexeme] = "DEFINED"
    
    def error(self, token: Token, message: str) -> None:
        self.errors.append(LoxSyntaxError.from_token(token, message))
        
    def push(self, **kwargs) -> Env:
        kwargs.setdefault("function_context", self.function_context)
        kwargs.setdefault("class_context", self.class_context)
        return Env(enclosing=self, errors=self.errors, **kwargs)

    def get_depth(self, name: str) -> int:
        if name in self.values or self.enclosing is None:
            return 0
        return 1 + self.enclosing.get_depth(name)

@singledispatch
def resolve_node(node: Expr | Stmt, env: Env) -> None:
    for child in vars(node).values():
        if isinstance(child, (Stmt, Expr, list)):
            resolve_node(child, env)

@resolve_node.register
def _(stmts: list, env: Env) -> None:
    for stmt in stmts:
        resolve_node(stmt, env)

@resolve_node.register
def _(stmt: Var, env: Env) -> None:
    env.declare(stmt.name)
    if stmt.initializer is not None:
        resolve_node(stmt.initializer, env)
    env.define(stmt.name)

@resolve_node.register
def _(expr: Variable, env: Env) -> None:
    if env.values.get(expr.name.lexeme) == "DECLARED":
        msg = "Can't read local variable in its own initializer."
        env.error(expr.name, msg)
    resolve_local(expr, expr.name, env)

@resolve_node.register
def _(expr: Assign, env: Env) -> None:
    resolve_node(expr.value, env)
    resolve_local(expr, expr.name, env)

@resolve_node.register
def _(stmt: Block, env: Env) -> None:
    resolve_node(stmt.statements, env.push())

@resolve_node.register
def _(stmt: Function, env: Env) -> None:
    env.declare(stmt.name)
    env.define(stmt.name)
    resolve_function(stmt, "FUNCTION", env)

@resolve_node.register
def _(stmt: Return, env: Env) -> None:
    if env.function_context is None: 
        env.error(stmt.keyword, "Can't return from top-level code.")
    if stmt.value is not None:
        if env.function_context == "INITIALIZER":
            msg = "Can't return a value from an initializer."
            env.error(stmt.keyword, msg)
        resolve_node(stmt.value, env)

@resolve_node.register
def _(stmt: Class, env: Env):
    env.declare(stmt.name)
    env.define(stmt.name)
    current_context = env.class_context
    env.class_context = "CLASS"

    if stmt.superclass is not None:
        resolve_node(stmt.superclass, env)
        env = env.push(class_context="SUBCLASS")
        env["super"] = "DEFINED"
    
        if stmt.name.lexeme == stmt.superclass.name.lexeme:
            msg = "A class can't inherit from itself."
            env.error(stmt.superclass.name, msg)

    for method in stmt.methods:
        role = "METHOD"
        if method.name.lexeme == "init":
            role = "INITIALIZER"
        method_env = env.push(function_context=role)
        method_env["this"] = "DEFINED"
        resolve_function(method, role, method_env)

    env.class_context = current_context

@resolve_node.register
def _(expr: This, env: Env) -> None:
    if env.class_context is None:
        msg = "Can't use 'this' outside of a class."
        env.error(expr.keyword, msg)
    resolve_local(expr, expr.keyword, env)

@resolve_node.register
def _(expr: Super, env: Env) -> None:
    if env.class_context is None:
        msg = "Can't use 'super' outside of a class."
        env.error(expr.keyword, msg)
    elif env.class_context != "SUBCLASS":
        msg = "Can't use 'super' in a class with no superclass."
        env.error(expr.keyword, msg)
    resolve_local(expr, expr.keyword, env)

def resolve_function(function: Function, type: FunctionContext, env: Env) -> None:
    env = env.push(function_context=type)
    for param in function.params:
        env.declare(param)
        env.define(param)
    resolve_node(function.body, env)

def resolve_local(expr: Expr, name: Token, env: Env) -> None:
    assert hasattr(expr, 'depth'), f"expr {expr.__class__.__name__} must have depth attribute"
    expr.depth = env.get_depth(name.lexeme)
