from dataclasses import dataclass, field
from lox.tokens import Token, TokenType
from lox.errors import LoxStaticError, LoxSyntaxError
from lox.ast import *


def parse(tokens: list[Token]) -> Stmt:
    parser = Parser(tokens)
    statements = []
    while not parser.is_at_end():
        try:
            statements.append(parser.declaration())
        except LoxSyntaxError:
            parser.synchronize()
    
    if parser.errors:
        raise LoxStaticError(parser.errors)
        
    return Program(statements)


@dataclass
class Parser:
    tokens: list[Token]
    current: int = 0
    errors: list[LoxSyntaxError] = field(default_factory=list)

    def __post_init__(self):
        for token in self.tokens:
            if token.type == "INVALID":
                self.error(token, "Unexpected character.")
        self.tokens = [t for t in self.tokens if t.type != "INVALID"]

    #
    # Grammar rules
    #
    def expression(self) -> Expr:
        return self.assignment()
    
    def assignment(self) -> Expr:
        expr = self.logic_or()
        if self.match("EQUAL"):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while self.match("OR"):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)
        return expr
    
    def logic_and(self) -> Expr:
        expr = self.equality()
        while self.match("AND"):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr
    
    def term(self) -> Expr:
        expr = self.factor()
        while self.match("MINUS", "PLUS"):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()
        while self.match("SLASH", "STAR"):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    
    def unary(self) -> Expr:
        if self.match("BANG", "MINUS"):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()
    
    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match("LEFT_PAREN"):
                expr = self.finish_call(expr)
            elif self.match("DOT"):
                msg = "Expect property name after '.'."
                name = self.consume("IDENTIFIER", msg)
                expr = Get(expr, name)
            else:
                break
        return expr
    
    def finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check("RIGHT_PAREN"):
            arguments.append(self.expression())
            while self.match("COMMA"):
                arguments.append(self.expression())
                if len(arguments) > 255:
                    self.error(self.previous(), "Can't have more than 255 arguments.")
        paren = self.consume("RIGHT_PAREN", "Expect ')' after arguments.")
        return Call(callee, paren, arguments)
    
    def super_expression(self) -> Super:
        keyword = self.consume("SUPER", "Expect 'super' keyword.")
        self.consume("DOT", "Expect '.' after 'super'.")
        method = self.consume("IDENTIFIER", "Expect superclass method name.")
        return Super(keyword, method)

    def primary(self) -> Expr:
        if self.match("FALSE"):
            return Literal(False)
        if self.match("TRUE"):
            return Literal(True)
        if self.match("NIL"):
            return Literal(None)
        if self.match("NUMBER", "STRING"):
            return Literal(self.previous().literal)
        if self.match("LEFT_PAREN"):
            expr = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return Grouping(expr)
        if self.match("IDENTIFIER"):
            return Variable(self.previous())
        if self.match("THIS"):
            return This(self.previous())
        if self.check("SUPER"):
            return self.super_expression()
        raise self.error(self.peek(), "Expect expression.")

    #
    # Statements
    #
    def declaration(self):
        match self.peek().type:
            case "VAR":
                return self.var_declaration()
            case "FUN":
                self.consume("FUN", "Expect function declaration.")
                return self.function("function")
            case "CLASS":
                return self.class_declaration()
            case _:
                return self.statement()
    
    def statement(self) -> Stmt:
        match self.peek().type:
            case "PRINT":
                return self.print_statement()
            case "LEFT_BRACE":
                return self.block_statement()
            case "IF":
                return self.if_statement()
            case "WHILE":
                return self.while_statement()
            case "FOR":
                return self.for_statement()
            case "RETURN":
                return self.return_statement()
            case _:
                return self.expression_statement()

    def print_statement(self) -> Stmt:
        self.consume("PRINT", "Expect 'print' keyword.")
        value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return Print(value)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume("SEMICOLON", "Expect ';' after expression.")
        return Expression(expr)
    
    def var_declaration(self) -> Var:
        self.consume("VAR", "Expect 'var' keyword.")
        name = self.consume("IDENTIFIER", "Expect variable name.")

        if self.match("EQUAL"):
            initializer = self.expression()
        else:
            initializer = Literal(None)

        self.consume("SEMICOLON", "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def block_statement(self) -> Block:
        self.consume("LEFT_BRACE", "Expect '{' to open block.")
        statements: list[Stmt] = []
        while not self.check("RIGHT_BRACE") and not self.is_at_end():
            statements.append(self.declaration())
        self.consume("RIGHT_BRACE", "Expect '}' after block.")
        return Block(statements)
    
    def if_statement(self) -> If:
        self.consume("IF", "Expect 'if'.")
        self.consume("LEFT_PAREN", "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)
    
    def while_statement(self) -> While:
        self.consume("WHILE", "Expect 'while'.")
        self.consume("LEFT_PAREN", "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)
    
    def for_statement(self):
        self.consume("FOR", "Expect 'for'.")
        self.consume("LEFT_PAREN", "Expect '(' after 'for'.")
        if self.match("SEMICOLON"):
            initializer = None
        elif self.check("VAR"):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check("SEMICOLON"):
            condition = self.expression()
        self.consume("SEMICOLON", "Expect ';' after loop condition.")
        increment = None
        if not self.check("RIGHT_PAREN"):
            increment = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after for clauses.")
        body = self.statement()
        
        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body
    
    def function(self, kind: str) -> Stmt:
        name = self.consume("IDENTIFIER", f"Expect {kind} name.")
        self.consume("LEFT_PAREN", f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check("RIGHT_PAREN"):
            argument = self.consume("IDENTIFIER", "Expect parameter name.")
            parameters.append(argument)
            while self.match("COMMA"):
                argument = self.consume("IDENTIFIER", "Expect parameter name.")
                parameters.append(argument)
                if len(parameters) > 255:
                    self.error(argument, "Can't have more than 255 parameters.")
        self.consume("RIGHT_PAREN", "Expect ')' after parameters.")
        if self.check("LEFT_BRACE"):
            body = self.block_statement()
        else:
            raise self.error(self.peek(), "Expect '{' before function body.")
        return Function(name, parameters, body.statements)

    def return_statement(self):
        keyword = self.consume("RETURN", "Expect 'return' keyword.")
        value = None
        if not self.check("SEMICOLON"):
            value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after return value.")
        return Return(keyword, value)

    def class_declaration(self) -> Class:
        self.consume("CLASS", "Expect 'class' keyword.")
        class_name = self.consume("IDENTIFIER", "Expect class name.")
        
        superclass = None
        if self.match("LESS"):
            name = self.consume("IDENTIFIER", "Expect superclass name.")
            superclass = Variable(name)

        methods = []
        self.consume("LEFT_BRACE", "Expect '{' before class body.")
        while not self.check("RIGHT_BRACE"):
            methods.append(self.function("method"))
        self.consume("RIGHT_BRACE", "Expect '}' after class body.")
        
        return Class(class_name, superclass, methods=methods)
    
    #
    # Utilities
    # 
    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        return not self.is_at_end() and self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().type == "EOF"

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str):
        error = LoxSyntaxError.from_token(token, message)
        self.errors.append(error)
        return error

    def synchronize(self):
        self.advance()
        boundary_tokens = {"CLASS", "FUN", "VAR", "FOR", "IF", "WHILE", "PRINT", "RETURN"}

        while not self.is_at_end():
            if self.previous().type == "SEMICOLON":
                return
            if self.peek().type in boundary_tokens:
                return
            self.advance()
