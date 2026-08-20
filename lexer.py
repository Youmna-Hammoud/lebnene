from enum import Enum

from errors import LebneneError

class TokenType(Enum):
    # Types
    RA2EM = "RA2EM"       # number
    KELME = "KELME"       # string

    # Keywords
    FARJINE = "FARJINE"   # print
    IZA = "IZA"           # if
    GHER_HEK = "GHER_HEK" # else
    TALAMA = "TALAMA"     # while
    LA = "LA"             # for
    REDELE = "REDELE"     # return
    ARREF = "ARREF"       # function definition
    SA7 = "SA7"           # true
    GHALAT = "GHALAT"     # false
    MASHI = "MASHI"       # null
    W = "W"               # and
    AW = "AW"             # or
    MISH = "MISH"         # not

    # Symbols
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COLON = "COLON"
    EQUALS = "EQUALS"
    EQUALS_EQUALS = "EQUALS_EQUALS"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUALS = "GREATER_EQUALS"
    LESS_EQUALS = "LESS_EQUALS"
    MISH_EQUALS = "MISH_EQUALS"
    MOD = "MOD"
    PLUS_EQUALS = "PLUS_EQUALS"
    MINUS_EQUALS = "MINUS_EQUALS"
    STAR_EQUALS = "STAR_EQUALS"
    SLASH_EQUALS = "SLASH_EQUALS"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    COMMA = "COMMA"

    # Other
    IDENTIFIER = "IDENTIFIER"
    EOF = "EOF"


KEYWORDS = {
    "farjine": TokenType.FARJINE,
    "iza":     TokenType.IZA,
    "gherhek": TokenType.GHER_HEK,
    "talama":  TokenType.TALAMA,
    "la":      TokenType.LA,
    "redele":  TokenType.REDELE,
    "3arref":  TokenType.ARREF,
    "sa7":     TokenType.SA7,
    "ghalat":  TokenType.GHALAT,
    "mashi":   TokenType.MASHI,
    "w":       TokenType.W,
    "aw":      TokenType.AW,
    "mish":    TokenType.MISH,
}


ESCAPES = {
    'n': '\n',
    't': '\t',
    '"': '"',
    '\\': '\\',
}


def unescape(raw):
    result = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == '\\' and i + 1 < len(raw) and raw[i + 1] in ESCAPES:
            result.append(ESCAPES[raw[i + 1]])
            i += 2
        else:
            result.append(c)
            i += 1
    return "".join(result)


class Token:
    def __init__(self, type, lexeme, value=None, line=1):
        self.type = type
        self.lexeme = lexeme
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, {self.value})"


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.indent_stack = [0]

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def add_token(self, type, value=None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(type, lexeme, value, self.line))

    def error(self, message):
        print(f"[satr {self.line}] Meshkle: {message}")

    def scan_token(self):
        c = self.advance()

        # Single character symbols
        if c == '(':
            self.add_token(TokenType.LPAREN)
        elif c == ')':
            self.add_token(TokenType.RPAREN)
        elif c == '{':
            self.add_token(TokenType.LBRACE)
        elif c == '}':
            self.add_token(TokenType.RBRACE)
        elif c == '[':
            self.add_token(TokenType.LBRACKET)
        elif c == ']':
            self.add_token(TokenType.RBRACKET)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '%':
            self.add_token(TokenType.MOD)

        # Two character symbols
        elif c == '+':
            self.add_token(TokenType.PLUS_EQUALS if self.match('=') else TokenType.PLUS)
        elif c == '-':
            self.add_token(TokenType.MINUS_EQUALS if self.match('=') else TokenType.MINUS)
        elif c == '*':
            self.add_token(TokenType.STAR_EQUALS if self.match('=') else TokenType.STAR)
        elif c == '=':
            self.add_token(
                TokenType.EQUALS_EQUALS if self.match('=')
                else TokenType.EQUALS
            )
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.MISH_EQUALS)
            else:
                self.error(f"Ma 3refet shou: {c!r}")
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUALS if self.match('=') else TokenType.GREATER)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUALS if self.match('=') else TokenType.LESS)

        # Comments / slash / compound-assign
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('='):
                self.add_token(TokenType.SLASH_EQUALS)
            else:
                self.add_token(TokenType.SLASH)

        # Whitespace
        elif c in (' ', '\r', '\t'):
            pass
        elif c == '\n':
            self.line += 1
            self.add_token(TokenType.NEWLINE)
            self.handle_indent()

        # Strings
        elif c == '"':
            self.string()

        # Numbers
        elif c.isdigit():
            if self.peek().isalpha() or self.peek() == '_':
                self.identifier()
            else:
                self.number()

        # Identifiers and keywords
        elif c.isalpha() or c == '_':
            self.identifier()

        else:
            self.error(f"Ma 3refet shou: {c!r}")

    def string(self):
        while not self.is_at_end() and self.peek() != '"':
            if self.peek() == '\\' and self.peek_next() != '\0':
                self.advance()  # backslash
                self.advance()  # escaped character, taken as-is (even if it's a quote)
                continue
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error("Kelme ma msakkara.")
            return

        self.advance()  # closing "
        raw = self.source[self.start + 1:self.current - 1]
        value = unescape(raw)
        self.add_token(TokenType.KELME, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
            value = float(self.source[self.start:self.current])
        else:
            value = int(self.source[self.start:self.current])
        
        self.add_token(TokenType.RA2EM, value)

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    # add new function to handle indentation
    def handle_indent(self):
        indent = 0
        while self.current < len(self.source) and self.source[self.current] in (' ', '\t'):
            indent += 1
            self.current += 1

        current_indent = self.indent_stack[-1]

        if indent > current_indent:
            self.indent_stack.append(indent)
            self.tokens.append(Token(TokenType.INDENT, "", None, self.line))
        elif indent < current_indent:
            while self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, "", None, self.line))
            if self.indent_stack[-1] != indent:
                raise LebneneError(
                    "Indentation mish mtabi2a (inconsistent indentation)", self.line
                )