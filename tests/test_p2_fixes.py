import pytest

from lexer import Lexer
from parser import Parser
from transpiler import Transpiler
from errors import LebneneError


def lex(source):
    return Lexer(source).scan_tokens()


def parse(source):
    return Parser(lex(source)).parse()


def transpile(source):
    return Transpiler(parse(source)).transpile()


def run(source, capsys):
    from lebnene import run as lebnene_run
    lebnene_run(source)
    return capsys.readouterr().out


# --- exec() sandboxing: restricted builtins ---

def test_dangerous_builtin_is_not_available(capsys):
    with pytest.raises(NameError):
        run('farjine(__import__("os"))', capsys)


def test_safe_builtins_still_work(capsys):
    assert run('farjine(len([1, 2, 3]))', capsys).strip() == "3"


def test_range_available_for_loops(capsys):
    out = run('la x, range(3):\n    farjine(x)\n', capsys)
    assert out.splitlines() == ["0", "1", "2"]


def test_str_int_float_available(capsys):
    assert run('farjine(str(5))', capsys).strip() == "5"
    assert run('farjine(int("5"))', capsys).strip() == "5"
    assert run('farjine(float("1.5"))', capsys).strip() == "1.5"


# --- consistent error types (LebneneError) ---

def test_parser_missing_paren_raises_lebnene_error():
    with pytest.raises(LebneneError):
        parse('farjine("hi"')


def test_parser_bad_token_raises_lebnene_error():
    with pytest.raises(LebneneError):
        parse('x = )')


def test_lexer_inconsistent_dedent_raises_lebnene_error():
    source = "iza sa7:\n    x = 1\n   y = 2\n"
    with pytest.raises(LebneneError):
        lex(source)


def test_lebnene_error_is_still_a_syntax_error():
    # backward compatibility: old code catching SyntaxError still works
    assert issubclass(LebneneError, SyntaxError)


def test_transpiler_unknown_statement_raises_lebnene_error():
    class FakeStatement:
        pass
    with pytest.raises(LebneneError):
        Transpiler([]).transpile_statement(FakeStatement())


def test_transpiler_unknown_expression_raises_lebnene_error():
    class FakeExpr:
        pass
    with pytest.raises(LebneneError):
        Transpiler([]).transpile_expression(FakeExpr())


# --- REPL multi-line input ---

def make_reader(lines):
    it = iter(lines)
    def read_line(prompt):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return read_line


def test_repl_single_line_yields_immediately():
    from lebnene import repl_lines
    results = list(repl_lines(make_reader(['farjine("hi")'])))
    assert results == ['farjine("hi")']


def test_repl_block_buffers_until_blank_line():
    from lebnene import repl_lines
    lines = [
        "iza sa7:",
        "    farjine(\"yes\")",
        "",
    ]
    results = list(repl_lines(make_reader(lines)))
    assert results == ["iza sa7:\n    farjine(\"yes\")\n"]


def test_repl_block_flushes_on_eof_without_blank_line():
    from lebnene import repl_lines
    lines = [
        "talama ghalat:",
        "    farjine(\"never\")",
    ]
    results = list(repl_lines(make_reader(lines)))
    assert results == ["talama ghalat:\n    farjine(\"never\")\n"]


def test_repl_multiple_statements_after_block():
    from lebnene import repl_lines
    lines = [
        "iza sa7:",
        "    farjine(\"yes\")",
        "",
        "farjine(\"after\")",
    ]
    results = list(repl_lines(make_reader(lines)))
    assert results == [
        "iza sa7:\n    farjine(\"yes\")\n",
        'farjine("after")',
    ]


def test_repl_block_actually_runs(capsys):
    source = "iza sa7:\n    farjine(\"yes\")\n"
    from lebnene import run as lebnene_run
    lebnene_run(source)
    assert capsys.readouterr().out.strip() == "yes"
