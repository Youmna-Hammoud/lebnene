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


def run(source, capsys):
    output = transpile(source)
    exec(output, {"__builtins__": __builtins__, "print": print})
    return capsys.readouterr().out


# --- elif (gherhek iza) ---

def test_elif_first_branch(capsys):
    source = (
        "x = 1\n"
        "iza x == 1:\n"
        "    farjine(\"one\")\n"
        "gherhek iza x == 2:\n"
        "    farjine(\"two\")\n"
        "gherhek:\n"
        "    farjine(\"other\")\n"
    )
    assert run(source, capsys).strip() == "one"


def test_elif_middle_branch(capsys):
    source = (
        "x = 2\n"
        "iza x == 1:\n"
        "    farjine(\"one\")\n"
        "gherhek iza x == 2:\n"
        "    farjine(\"two\")\n"
        "gherhek:\n"
        "    farjine(\"other\")\n"
    )
    assert run(source, capsys).strip() == "two"


def test_elif_fallthrough_else(capsys):
    source = (
        "x = 99\n"
        "iza x == 1:\n"
        "    farjine(\"one\")\n"
        "gherhek iza x == 2:\n"
        "    farjine(\"two\")\n"
        "gherhek:\n"
        "    farjine(\"other\")\n"
    )
    assert run(source, capsys).strip() == "other"


# --- unary minus ---

def test_unary_minus_literal(capsys):
    assert run('farjine(-5)', capsys).strip() == "-5"


def test_unary_minus_double_negative(capsys):
    assert run('farjine(5 - -3)', capsys).strip() == "8"


def test_unary_minus_on_variable(capsys):
    assert run('x = 5\nfarjine(-x)', capsys).strip() == "-5"


# --- >= and <= ---

def test_greater_equal_true(capsys):
    assert run('farjine(3 >= 3)', capsys).strip() == "True"


def test_less_equal_false(capsys):
    assert run('farjine(5 <= 3)', capsys).strip() == "False"


def test_greater_still_works(capsys):
    assert run('farjine(5 > 3)', capsys).strip() == "True"


# --- modulo ---

def test_modulo(capsys):
    assert run('farjine(10 % 3)', capsys).strip() == "1"


# --- compound assignment ---

def test_plus_equals(capsys):
    assert run('x = 5\nx += 3\nfarjine(x)', capsys).strip() == "8"


def test_minus_equals(capsys):
    assert run('x = 5\nx -= 3\nfarjine(x)', capsys).strip() == "2"


def test_star_equals(capsys):
    assert run('x = 5\nx *= 3\nfarjine(x)', capsys).strip() == "15"


def test_slash_equals(capsys):
    assert run('x = 6\nx /= 3\nfarjine(x)', capsys).strip() == "2.0"


def test_plain_equals_still_works(capsys):
    assert run('x = 5\nfarjine(x)', capsys).strip() == "5"


# --- string escapes ---

def test_newline_escape(capsys):
    out = run('farjine("line1\\nline2")', capsys)
    assert out.splitlines() == ["line1", "line2"]


def test_tab_escape(capsys):
    out = run('farjine("a\\tb")', capsys)
    assert out.strip("\n") == "a\tb"


def test_escaped_quote(capsys):
    out = run('farjine("she said \\"hi\\"")', capsys)
    assert out.strip() == 'she said "hi"'


def test_escaped_backslash(capsys):
    out = run('farjine("a\\\\b")', capsys)
    assert out.strip() == "a\\b"


def test_plain_string_still_works(capsys):
    assert run('farjine("marhaba")', capsys).strip() == "marhaba"
