from functools import singledispatch

from lox.ast import Binary, Expr, Grouping, Literal, Unary
from lox.tokens import Token


@singledispatch
def pretty(expr: Expr) -> str:
    raise TypeError(f"cannot display {expr.__class__.__name__} objects")


@pretty.register
def _(expr: Binary):
    symbol = expr.operator.lexeme
    return parenthesize(symbol, expr.left, expr.right)


@pretty.register
def _(expr: Grouping):
    return parenthesize("group", expr.expression)


@pretty.register
def _(expr: Literal):
    if expr.value is None:
        return "nil"
    elif expr.value is True:
        return "true"
    elif expr.value is False:
        return "false"
    return str(expr.value)


@pretty.register
def _(expr: Unary):
    symbol = expr.operator.lexeme
    return parenthesize(symbol, expr.right)


def parenthesize(name: str, *exprs: Expr) -> str:
    parts = [name, *map(pretty, exprs)]
    return "(" + " ".join(parts) + ")"


def main():
    minus = Token("MINUS", "-", 1)
    star = Token("STAR", "*", 1)
    expr = Binary(Unary(minus, Literal(123)), star, Grouping(Literal(45.67)))
    print(pretty(expr))


if __name__ == "__main__":
    main()
