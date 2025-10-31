from dataclasses import dataclass
from turtle import distance
from typing import Any

from lox.tokens import Token


class Expr:
    """Abstract Base Class for expressions"""


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Grouping(Expr):
    expression: Expr


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass
class Variable(Expr):
    name: Token
    depth: int = -1


# lox/ast.py
@dataclass
class Assign(Expr):
    name: Token
    value: Expr
    depth: int = -1


@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

@dataclass
class Get(Expr):
    object: Expr
    name: Token

@dataclass
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

@dataclass
class This(Expr):
    keyword: Token
    depth: int = -1

@dataclass
class Super(Expr):
    keyword: Token
    method: Token
    depth: int = -1

class Stmt:
    """Abstract Base Class for statements"""


@dataclass
class Program(Stmt):
    statements: list[Stmt]


@dataclass
class Expression(Stmt):
    expression: Expr


@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

@dataclass
class Block(Stmt):
    statements: list[Stmt]

@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

@dataclass
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

@dataclass
class Return(Stmt):
    keyword: Token
    value: Expr | None

@dataclass
class Class(Stmt):
    name: Token
    superclass: Variable | None
    methods: list[Function]

