from functools import singledispatch
from tkinter import E
from typing import Any
from .expr import *
from .tokens import TokenType as TT
from .errors import LoxRuntimeError

type Environment = Any  # Placeholder for future Environment class

@singledispatch
def eval(expr: Expr, env: Environment) -> Any:
    msg = f"cannot eval {expr.__class__.__name__} objects"
    raise TypeError(msg)

@eval.register
def _(expr: Literal, env) -> Any:
    return expr.value

@eval.register
def _(expr: Grouping, env):
    return eval(expr.expression, env)

@eval.register
def _(expr: Unary, env):
    right = eval(expr.right, env)

    match expr.operator.type :
        case TT.MINUS:
            return -as_number_operand(expr.operator, right)
        case TT.BANG:
            return not is_truthy(right)
    # Unreachable.

@eval.register
def _(expr: Binary, env):
    left = eval(expr.left, env)
    right = eval(expr.right, env)

    match expr.operator.type :
        case TT.MINUS:
            check_number_operands(expr.operator, left, right)
            return left - right
        case TT.SLASH:
            check_number_operands(expr.operator, left, right)
            return left / right
        case TT.STAR:
            check_number_operands(expr.operator, left, right)
            return left * right
        case TT.PLUS:
            if type(left) == type(right) and type(left) in (float, str):
                return left + right
            raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings")
        case TT.GREATER:
            check_number_operands(expr.operator, left, right)
            return left > right
        case TT.GREATER_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left >= right
        case TT.LESS:
            check_number_operands(expr.operator, left, right)
            return left < right
        case TT.LESS_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left <= right


def is_truthy(obj: Any) -> bool:
    if obj is None or obj is False:
        return False
    return True

def as_number_operand(operator: Token, operand: Any) -> float:
    if isinstance(operand, float):
        return operand
    raise LoxRuntimeError(operator, "Operand must be a number")


def check_number_operands(operator: Token, left: Any, right: Any) -> None:
    if isinstance(left, float) and isinstance(right, float):
        return
    raise LoxRuntimeError(operator, "Operands must be numbers")