from dataclasses import dataclass, field
from typing import Any

from lox.tokens import Token, TokenType
from lox.errors import LoxSyntaxError

KEYWORDS = {
    "and",
    "class",
    "else",
    "false",
    "for",
    "fun",
    "if",
    "nil",
    "or",
    "print",
    "return",
    "super",
    "this",
    "true",
    "var",
    "while",
}


@dataclass
class Scanner:
    source: str
    start: int = 0
    current: int = 0
    line: int = 1
    tokens: list[Token] = field(default_factory=list)

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            # We are at the beginning of the next lexeme.
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token("EOF", "", self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self):
        match self.advance():
            case "(":
                self.add_token("LEFT_PAREN")
            case ")":
                self.add_token("RIGHT_PAREN")
            case "{":
                self.add_token("LEFT_BRACE")
            case "}":
                self.add_token("RIGHT_BRACE")
            case ",":
                self.add_token("COMMA")
            case ".":
                self.add_token("DOT")
            case "-":
                self.add_token("MINUS")
            case "+":
                self.add_token("PLUS")
            case ";":
                self.add_token("SEMICOLON")
            case "*":
                self.add_token("STAR")
            case "!" if self.match("="):
                self.add_token("BANG_EQUAL")
            case "!":
                self.add_token("BANG")
            case "=" if self.match("="):
                self.add_token("EQUAL_EQUAL")
            case "=":
                self.add_token("EQUAL")
            case "<" if self.match("="):
                self.add_token("LESS_EQUAL")
            case "<":
                self.add_token("LESS")
            case ">" if self.match("="):
                self.add_token("GREATER_EQUAL")
            case ">":
                self.add_token("GREATER")
            case "/" if self.match("/"):
                # A comment goes until the end of the line.
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            case "/":
                self.add_token("SLASH")
            case " " | "\r" | "\t":
                pass  # Ignore whitespace.
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                self.number()
            case c if is_alpha(c):
                self.identifier()
            case _:
                self.add_token("INVALID")

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, self.line, literal))

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return ""
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        # FIX THIS
        if self.is_at_end():
            raise LoxSyntaxError(self.line, "Unterminated string.")

        # The closing ".
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token("STRING", value)

    def number(self):
        while is_digit(self.peek()):
            self.advance()

        # Look for a fractional part.
        if self.peek() == "." and is_digit(self.peek_next()):
            # Consume the "."
            self.advance()

        while is_digit(self.peek()):
            self.advance()

        substring = self.source[self.start : self.current]
        self.add_token("NUMBER", float(substring))

    def identifier(self):
        while is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source[self.start : self.current]
        kind = "IDENTIFIER"
        if text in KEYWORDS:
            kind = text.upper()
        self.add_token(kind)


def is_digit(char: str) -> bool:
    return char.isdigit() and char.isascii()


def is_alpha(char: str) -> bool:
    return char == "_" or char.isalpha() and char.isascii()


def is_alpha_numeric(char: str) -> bool:
    return is_alpha(char) or is_digit(char)


def tokenize(source: str) -> list[Token]:
    scanner = Scanner(source)
    return scanner.scan_tokens()
