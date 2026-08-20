from lexer import TokenType
from errors import LebneneError
from ast_nodes import (
    PrintStatement, IfStatement, AssignStatement,
    BinaryExpr, LiteralExpr, IdentifierExpr, WhileStatement, FunctionDef, CallExpr, ReturnStatement,
    UnaryExpr, ListExpr, IndexExpr, ForStatement
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
        raise LebneneError(message, self.peek().line)
    
    def parse(self):
        statements = []
        while not self.is_at_end():
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def statement(self):
        while self.match(TokenType.NEWLINE):
            pass
        
        if self.is_at_end():
            return None
        if self.match(TokenType.FARJINE):
            return self.print_statement()
        if self.match(TokenType.IZA):
            return self.if_statement()
        if self.match(TokenType.TALAMA):
            return self.while_statement()
        if self.match(TokenType.LA):
            return self.for_statement()
        if self.match(TokenType.ARREF):
            return self.function_def()
        if self.match(TokenType.REDELE):
            return self.return_statement()
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
            if self.match(TokenType.IZA):
                else_body = [self.if_statement()]  # gherhek iza ... == elif
            else:
                self.expect(TokenType.COLON, "Lezem ':' ba3d gherhek")
                else_body = self.block()

        return IfStatement(condition, body, else_body)

    ASSIGN_OPERATORS = (
        TokenType.EQUALS, TokenType.PLUS_EQUALS, TokenType.MINUS_EQUALS,
        TokenType.STAR_EQUALS, TokenType.SLASH_EQUALS,
    )

    def assign_statement(self):
        name = self.expect(TokenType.IDENTIFIER, "Lezem identifier")
        if not self.match(*self.ASSIGN_OPERATORS):
            raise LebneneError("Lezem '='", self.peek().line)
        operator = self.tokens[self.current - 1].lexeme
        value = self.expression()
        return AssignStatement(name.lexeme, value, operator)

    def block(self):
        statements = []
        self.expect(TokenType.NEWLINE, "Lezem satr jdid ba3d ':'")
        self.expect(TokenType.INDENT, "Lezem indent")
        
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            while self.match(TokenType.NEWLINE):  # skip newlines inside block
                pass
            if self.check(TokenType.DEDENT) or self.is_at_end():
                break
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
                
        self.match(TokenType.DEDENT)
        return statements

    def expression(self):
        return self.logic_or()

    def logic_or(self):
        left = self.logic_and()
        while self.match(TokenType.AW):
            operator = self.tokens[self.current - 1]
            right = self.logic_and()
            left = BinaryExpr(left, operator, right)
        return left

    def logic_and(self):
        left = self.logic_not()
        while self.match(TokenType.W):
            operator = self.tokens[self.current - 1]
            right = self.logic_not()
            left = BinaryExpr(left, operator, right)
        return left

    def logic_not(self):
        if self.match(TokenType.MISH):
            operator = self.tokens[self.current - 1]
            operand = self.logic_not()
            return UnaryExpr(operator, operand)
        return self.comparison()

    def comparison(self):
        left = self.addition()
        while self.match(TokenType.EQUALS_EQUALS, TokenType.MISH_EQUALS,
                         TokenType.GREATER, TokenType.LESS,
                         TokenType.GREATER_EQUALS, TokenType.LESS_EQUALS):
            operator = self.tokens[self.current - 1]
            right = self.addition()
            left = BinaryExpr(left, operator, right)
        return left

    def term(self):
        expr = self.primary()
        while self.match(TokenType.LBRACKET):
            index = self.expression()
            self.expect(TokenType.RBRACKET, "Lezem ']' ba3d l index")
            expr = IndexExpr(expr, index)
        return expr

    def primary(self):
        token = self.peek()

        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    elements.append(self.expression())
            self.expect(TokenType.RBRACKET, "Lezem ']' ba3d l list")
            return ListExpr(elements)
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
            name = self.tokens[self.current - 1].lexeme
            if self.match(TokenType.LPAREN):      # is it a call?
                return self.call_expr(name)
            return IdentifierExpr(name)

        raise LebneneError(f"Ma 3refet shou: {token.lexeme!r}", token.line)

    def addition(self):
        left = self.multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.tokens[self.current - 1]
            right = self.multiplication()
            left = BinaryExpr(left, operator, right)
        
        return left

    def multiplication(self):
        left = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.MOD):
            operator = self.tokens[self.current - 1]
            right = self.unary()
            left = BinaryExpr(left, operator, right)

        return left

    def unary(self):
        if self.match(TokenType.MINUS):
            operator = self.tokens[self.current - 1]
            operand = self.unary()
            return UnaryExpr(operator, operand)
        return self.term()

    def while_statement(self):
        condition = self.expression()
        self.expect(TokenType.COLON, "Lezem ':' ba3d talama")
        body = self.block()
        return WhileStatement(condition, body)

    def for_statement(self):
        name = self.expect(TokenType.IDENTIFIER, "Lezem ism l variable ba3d la")
        self.expect(TokenType.COMMA, "Lezem ',' ba3d ism l variable")
        iterable = self.expression()
        self.expect(TokenType.COLON, "Lezem ':' ba3d l iterable")
        body = self.block()
        return ForStatement(name.lexeme, iterable, body)

    def function_def(self):
        name = self.expect(TokenType.IDENTIFIER, "Lezem ism l function")
        self.expect(TokenType.LPAREN, "Lezem '(' ba3d ism l function")

        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.expect(TokenType.IDENTIFIER, "Lezem ism l parameter").lexeme)
            while self.match(TokenType.COMMA):
                params.append(self.expect(TokenType.IDENTIFIER, "Lezem ism l parameter").lexeme)

        self.expect(TokenType.RPAREN, "Lezem ')' ba3d l parameters")
        self.expect(TokenType.COLON, "Lezem ':' ba3d l function")
        body = self.block()

        return FunctionDef(name.lexeme, params, body)

    def return_statement(self):
        value = self.expression()
        return ReturnStatement(value)

    def call_expr(self, name):
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.expression())
            while self.match(TokenType.COMMA):
                args.append(self.expression())
        
        self.expect(TokenType.RPAREN, "Lezem ')' ba3d l arguments")
        return CallExpr(name, args)