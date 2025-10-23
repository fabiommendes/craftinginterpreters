from dataclasses import dataclass

from .types import TokenType, Value

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    literal: Value = None

    def __str__(self):
        return f"{self.type.name} {self.lexeme!r} {self.literal}"
