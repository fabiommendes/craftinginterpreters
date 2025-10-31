from dataclasses import dataclass
from typing import Literal


type LiteralValue = str | float | bool | None
type TokenType = Literal[
    # Single-character tokens.
    "LEFT_PAREN", 
    "RIGHT_PAREN", 
    "LEFT_BRACE", 
    "RIGHT_BRACE", 
    "COMMA", 
    "DOT", 
    "SEMICOLON", 
    "MINUS", 
    "PLUS", 
    "SLASH", 
    "STAR", 

    # One or two character tokens.
    "BANG", 
    "BANG_EQUAL", 
    "EQUAL", 
    "EQUAL_EQUAL", 
    "GREATER", 
    "GREATER_EQUAL", 
    "LESS", 
    "LESS_EQUAL", 

    # Literals.
    "IDENTIFIER", 
    "STRING", 
    "NUMBER", 

    # Keywords.
    "AND", 
    "CLASS", 
    "ELSE", 
    "FALSE", 
    "FUN", 
    "FOR", 
    "IF", 
    "NIL", 
    "OR", 
    "PRINT", 
    "RETURN", 
    "SUPER", 
    "THIS", 
    "TRUE", 
    "VAR", 
    "WHILE", 

    # Special tokens.
    "EOF", 
    "INVALID", 
    "UNTERMINATED_STRING", 
]

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    literal: LiteralValue = None

    def __str__(self):
        return f"{self.type} {self.lexeme!r} {self.literal}"


