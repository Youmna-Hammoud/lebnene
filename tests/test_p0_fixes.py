import pytest

from lexer import Lexer, TokenType
from parser import Parser
from transpiler import Transpiler


def lex(source):
    return Lexer(source).scan_tokens()


def parse(source):
    return Parser(lex(source)).parse()


def transpile(source):
    return Transpiler(parse(source)).transpile()


# --- (1) standalone '!' must not emit a token with type=None ---

def test_standalone_bang_does_not_emit_none_type_token():
    tokens = lex("!")
    assert all(t.type is not None for t in tokens)


def test_not_equals_still_lexes_correctly():
    tokens = lex("x != y")
    types = [t.type for t in tokens]
    assert TokenType.MISH_EQUALS in types
    assert None not in types


# --- (2) w / aw / mish wired into the parser grammar ---

def test_logical_and_transpiles_and_evaluates(capsys):
    output = transpile('farjine(sa7 w ghalat)')
    assert "and" in output
    exec(output, {"__builtins__": __builtins__, "print": print})
    assert capsys.readouterr().out.strip() == "False"


def test_logical_or_transpiles_and_evaluates(capsys):
    output = transpile('farjine(sa7 aw ghalat)')
    assert "or" in output
    exec(output, {"__builtins__": __builtins__, "print": print})
    assert capsys.readouterr().out.strip() == "True"


def test_logical_not_transpiles_and_evaluates(capsys):
    output = transpile('farjine(mish ghalat)')
    assert "not" in output
    exec(output, {"__builtins__": __builtins__, "print": print})
    assert capsys.readouterr().out.strip() == "True"


def test_not_binds_tighter_than_and(capsys):
    # (mish sa7) w ghalat  ==  (not True) and False  ==  False
    output = transpile('farjine(mish sa7 w ghalat)')
    exec(output, {"__builtins__": __builtins__, "print": print})
    assert capsys.readouterr().out.strip() == "False"


# --- (3) indentation dedent must be validated against the indent stack ---

def test_inconsistent_dedent_raises_syntax_error():
    source = "iza sa7:\n    x = 1\n   y = 2\n"  # dedents to 3, but stack only has 0 and 4
    with pytest.raises(SyntaxError):
        lex(source)


def test_consistent_dedent_does_not_raise():
    source = "iza sa7:\n    x = 1\ny = 2\n"  # dedents cleanly back to 0
    lex(source)  # should not raise


# --- (4) tabs must be counted as indentation ---

def test_tab_indentation_produces_indent_token():
    source = "iza sa7:\n\tfarjine(\"hi\")\n"
    tokens = lex(source)
    assert TokenType.INDENT in [t.type for t in tokens]


def test_tab_indented_block_parses():
    source = "iza sa7:\n\tfarjine(\"hi\")\n"
    parse(source)  # should not raise
