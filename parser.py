from lexer import TokenType
from ast_nodes import (
    PrintStatement, IfStatement, AssignStatement,
    BinaryExpr, LiteralExpr, IdentifierExpr
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        return self.tokens[self.current]

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def expect(self, type, message):
        if self.check(type):
            return self.advance()
        raise SyntaxError(f"[satr {self.peek().line}] {message}")
    
    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.match(TokenType.FARJINE):
            return self.print_statement()
        if self.match(TokenType.IZA):
            return self.if_statement()
        return self.assign_statement()

    def print_statement(self):
        self.expect(TokenType.LPAREN, "Lezem '(' ba3d farjine")
        expr = self.expression()
        self.expect(TokenType.RPAREN, "Lezem ')' ba3d l expression")
        return PrintStatement(expr)

    def if_statement(self):
        condition = self.expression()
        self.expect(TokenType.COLON, "Lezem ':' ba3d l condition")
        body = self.block()
        
        else_body = None
        if self.match(TokenType.GHER_HEK):
            self.expect(TokenType.COLON, "Lezem ':' ba3d gherhek")
            else_body = self.block()
        
        return IfStatement(condition, body, else_body)

    def assign_statement(self):
        name = self.expect(TokenType.IDENTIFIER, "Lezem identifier")
        self.expect(TokenType.EQUALS, "Lezem '='")
        value = self.expression()
        return AssignStatement(name.lexeme, value)

    def block(self):
        statements = []
        self.expect(TokenType.NEWLINE, "Lezem satr jdid ba3d ':'")
        self.expect(TokenType.INDENT, "Lezem indent")
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            statements.append(self.statement())
        self.match(TokenType.DEDENT)
        return statements

    def expression(self):
        return self.comparison()

    def comparison(self):
        left = self.term()
        while self.match(TokenType.EQUALS_EQUALS, TokenType.MISH_EQUALS,
                         TokenType.GREATER, TokenType.LESS):
            operator = self.tokens[self.current - 1]
            right = self.term()
            left = BinaryExpr(left, operator, right)
        return left

    def term(self):
        token = self.peek()
        
        if self.match(TokenType.KELME):
            return LiteralExpr(self.tokens[self.current - 1].value)
        if self.match(TokenType.RA2EM):
            return LiteralExpr(self.tokens[self.current - 1].value)
        if self.match(TokenType.SA7):
            return LiteralExpr(True)
        if self.match(TokenType.GHALAT):
            return LiteralExpr(False)
        if self.match(TokenType.MASHI):
            return LiteralExpr(None)
        if self.match(TokenType.IDENTIFIER):
            return IdentifierExpr(self.tokens[self.current - 1].lexeme)
        
        raise SyntaxError(f"[satr {token.line}] Ma 3refet shou: {token.lexeme!r}")