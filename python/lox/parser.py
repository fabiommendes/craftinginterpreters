from dataclasses import dataclass
from lib2to3.pgen2.parse import ParseError
from .tokens import Token, TokenType as TT
from .expr import *

def parse(tokens: list[Token]) -> Expr | None:
    parser = Parser(tokens)
    try:
        return parser.expression()
    except ParseError:
        return None


@dataclass
class Parser:
    tokens: list[Token]
    current: int = 0

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None

    def expression(self) -> Expr:
        return self.equality()
    
    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr
    
    def match(self, *types: TT) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TT) -> bool:
        return not self.is_at_end() and self.peek().type == type

    def advance(self, type: TT) -> bool:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().type == TT.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(TT.GREATER, TT.GREATER_EQUAL, TT.LESS,
                        TT.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr
    
    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TT.MINUS, TT.PLUS):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TT.SLASH, TT.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self) -> Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()
    
    def primary(self) -> Expr:
        if self.match(TT.FALSE):
            return Literal(False)
        if self.match(TT.TRUE):
            return Literal(True)
        if self.match(TT.NIL):
            return Literal(None)
        if self.match(TT.NUMBER, TT.STRING):
            return Literal(self.previous().literal)
        if self.match(TT.LEFT_PAREN):
            expr = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise ParseError(self.peek(), "Expect expression.")
        
    def consume(self, type: TT, message: str):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str):
        return ParseError(token, message)
    
    def error(self, token: Token,  message: str):
        if token.type == TT.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "'", message)

    def synchronize(self):
        self.advance()
        boundary_tokens = {TT.CLASS, TT.FUN, TT.VAR, TT.FOR, TT.IF,
                        TT.WHILE, TT.PRINT, TT.RETURN}

        while not self.is_at_end():
            if self.previous().type == TT.SEMICOLON:
                return
            if self.peek().type in boundary_tokens:
                return
        self.advance()

class ParseError(RuntimeError):
    pass