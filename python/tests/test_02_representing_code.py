"""
This test module assumes the AST types Binary, Grouping, Literal and Unary with
thoses exact names and with behaviour and signatures as defined in the book.
"""

from pathlib import Path

from lox.ast import Binary, Expr, Grouping, Literal, Unary
from lox.printer import pretty
from lox.tokens import Token
from lox.tokens import TokenType as TT

TEST_BASE = Path(__file__).parent.parent / "examples" / "scanning"


class TestRepresentation:
    OPERATORS = {
        "!": "BANG",
        "!=": "BANG_EQUAL",
        "==": "EQUAL_EQUAL",
        ">": "GREATER",
        ">=": "GREATER_EQUAL",
        "<": "LESS",
        "<=": "LESS_EQUAL",
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "and": "AND",
        "or": "OR",
    }

    def op(self, symbol: str, lineno: int = 1):
        type = self.OPERATORS[symbol]
        return Token(type, symbol, lineno)

    def expr(self, value):
        if isinstance(value, Expr):
            return value
        elif value in (None, True, False):
            return Literal(value)
        else:
            raise TypeError(f"cannot convert {value!r} to Expr")

    def binary(self, left, op: str, right, lineno: int = 1):
        left = self.expr(left)
        right = self.expr(right)
        return Binary(left, self.op(op, lineno), right)

    def unary(self, op: str, right, lineno: int = 1):
        right = self.expr(right)
        return Unary(self.op(op, lineno), right)

    def test_not_bool(self):
        assert pretty(self.unary("!", True)) == "(! true)"
        assert pretty(self.unary("!", False)) == "(! false)"

    def test_binary_operations(self):
        assert pretty(self.binary(True, "+", False)) == "(+ true false)"
        assert pretty(self.binary(True, "and", False)) == "(and true false)"
        assert pretty(self.binary(True, "or", False)) == "(or true false)"

    def test_nested(self):
        expr = self.binary(
            self.unary("!", True),
            "==",
            self.binary(False, "!=", None),
        )
        assert pretty(expr) == "(== (! true) (!= false nil))"

    def test_grouping(self):
        expr = Grouping(
            self.binary(
                self.unary("!", True),
                "==",
                self.binary(False, "!=", None),
            )
        )
        assert pretty(expr) == "(group (== (! true) (!= false nil)))"
