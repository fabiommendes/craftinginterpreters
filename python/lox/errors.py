from __future__ import annotations
from lox.tokens import Token

class LoxSyntaxError(Exception):
    @classmethod
    def from_token(cls, token: Token, message: str) -> LoxSyntaxError:
        where =  "at end" if token.type == "EOF" else f"at '{token.lexeme}'"
        return cls(token.line, message, where)

    def __init__(self, line: int, message: str, where: str | None = None):
        super().__init__(line, message, where)
        self.line = line
        self.message = message
        self.where = where

    def __str__(self):
        if self.where is None:
            where = ""
        else:
            where = f" {self.where}"
        return f"[line {self.line}] Error{where}: {self.message}"

class LoxRuntimeError(Exception):
    def __init__(self, message: str, token: Token):
        super().__init__(message)
        assert isinstance(token, Token)
        self.token = token
        self.message = message

    def __str__(self) -> str:
        prefix =  f"[line {self.token.line}] "
        prefix += f"Runtime error at '{self.token.lexeme}'"
        return f"{prefix}: {self.message}"


class LoxStaticError(Exception):
    def __init__(self, errors: list[LoxSyntaxError]):
        self.errors = errors

    def __str__(self):
        return "\n".join(str(error) for error in self.errors)
    
    