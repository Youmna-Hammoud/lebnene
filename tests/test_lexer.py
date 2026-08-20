from lexer import Lexer, TokenType, KEYWORDS


def lex(source):
    return Lexer(source).scan_tokens()


def test_function_def_source_tokenizes_correctly():
    source = '''
3arref jam3(a, b):
    redele a + b

x = jam3(3, 4)
farjine(x)
'''
    tokens = lex(source)
    types = [t.type for t in tokens]
    assert types == [
        TokenType.NEWLINE,
        TokenType.ARREF, TokenType.IDENTIFIER, TokenType.LPAREN,
        TokenType.IDENTIFIER, TokenType.COMMA, TokenType.IDENTIFIER,
        TokenType.RPAREN, TokenType.COLON, TokenType.NEWLINE, TokenType.INDENT,
        TokenType.REDELE, TokenType.IDENTIFIER, TokenType.PLUS,
        TokenType.IDENTIFIER, TokenType.NEWLINE, TokenType.DEDENT,
        TokenType.NEWLINE,
        TokenType.IDENTIFIER, TokenType.EQUALS, TokenType.IDENTIFIER,
        TokenType.LPAREN, TokenType.RA2EM, TokenType.COMMA, TokenType.RA2EM,
        TokenType.RPAREN, TokenType.NEWLINE,
        TokenType.FARJINE, TokenType.LPAREN, TokenType.IDENTIFIER,
        TokenType.RPAREN, TokenType.NEWLINE,
        TokenType.EOF,
    ]


def test_number_literal_value():
    tokens = lex("42")
    assert tokens[0].type == TokenType.RA2EM
    assert tokens[0].value == 42


def test_float_literal_value():
    tokens = lex("3.5")
    assert tokens[0].type == TokenType.RA2EM
    assert tokens[0].value == 3.5


def test_string_literal_value():
    tokens = lex('"marhaba"')
    assert tokens[0].type == TokenType.KELME
    assert tokens[0].value == "marhaba"


def test_identifier_not_mistaken_for_keyword():
    tokens = lex("farjinet")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "farjinet"


def test_every_keyword_lexes_to_its_token_type():
    for text, expected_type in KEYWORDS.items():
        tokens = lex(text)
        assert tokens[0].type == expected_type, f"{text!r} lexed as {tokens[0].type}"


def test_source_always_ends_with_eof_token():
    tokens = lex("x = 1")
    assert tokens[-1].type == TokenType.EOF
