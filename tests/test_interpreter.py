import glob
import os

import pytest

from lexer import Lexer
from parser import Parser
from transpiler import Transpiler
from interpreter import Interpreter
from errors import LebneneError


def parse(source):
    return Parser(Lexer(source).scan_tokens()).parse()


def interpret(source, capsys):
    statements = parse(source)
    Interpreter(statements).run()
    return capsys.readouterr().out


def transpile_and_run(source, capsys):
    statements = parse(source)
    output = Transpiler(statements).transpile()
    from lebnene import SAFE_BUILTINS, lebnene_print
    exec(output, {"__builtins__": SAFE_BUILTINS, "print": lebnene_print})
    return capsys.readouterr().out


# --- basics ---

def test_print_literal(capsys):
    assert interpret('farjine("marhaba")', capsys).strip() == "marhaba"


def test_arithmetic(capsys):
    assert interpret('farjine(2 + 3 * 4)', capsys).strip() == "14"


def test_boolean_printing(capsys):
    assert interpret('farjine(sa7)', capsys).strip() == "sa7"
    assert interpret('farjine(ghalat)', capsys).strip() == "ghalat"
    assert interpret('farjine(mashi)', capsys).strip() == "mashi"


def test_assignment_and_reference(capsys):
    assert interpret('x = 42\nfarjine(x)', capsys).strip() == "42"


def test_compound_assignment(capsys):
    assert interpret('x = 5\nx += 3\nfarjine(x)', capsys).strip() == "8"


def test_unary_minus(capsys):
    assert interpret('farjine(-5)', capsys).strip() == "-5"


# --- control flow ---

def test_if_else(capsys):
    out = interpret('iza ghalat:\n    farjine("a")\ngherhek:\n    farjine("b")\n', capsys)
    assert out.strip() == "b"


def test_elif_chain(capsys):
    source = (
        "x = 2\n"
        "iza x == 1:\n    farjine(\"one\")\n"
        "gherhek iza x == 2:\n    farjine(\"two\")\n"
        "gherhek:\n    farjine(\"other\")\n"
    )
    assert interpret(source, capsys).strip() == "two"


def test_while_loop(capsys):
    source = "x = 0\ntotal = 0\ntalama x < 5:\n    total = total + x\n    x = x + 1\nfarjine(total)\n"
    assert interpret(source, capsys).strip() == "10"


def test_for_loop(capsys):
    out = interpret('la x, [1, 2, 3]:\n    farjine(x)\n', capsys)
    assert out.splitlines() == ["1", "2", "3"]


def test_logical_and_or_not(capsys):
    assert interpret('farjine(sa7 w ghalat)', capsys).strip() == "ghalat"
    assert interpret('farjine(sa7 aw ghalat)', capsys).strip() == "sa7"
    assert interpret('farjine(mish ghalat)', capsys).strip() == "sa7"


# --- functions ---

def test_function_call(capsys):
    source = "3arref jam3(a, b):\n    redele a + b\nfarjine(jam3(3, 4))\n"
    assert interpret(source, capsys).strip() == "7"


def test_recursive_function(capsys):
    source = (
        "3arref fact(n):\n"
        "    iza n == 0:\n        redele 1\n"
        "    gherhek:\n        redele n * fact(n - 1)\n"
        "farjine(fact(5))\n"
    )
    assert interpret(source, capsys).strip() == "120"


def test_function_local_scope_does_not_leak(capsys):
    source = (
        "x = 100\n"
        "3arref f():\n"
        "    x = 1\n"
        "    redele x\n"
        "farjine(f())\n"
        "farjine(x)\n"
    )
    assert interpret(source, capsys).splitlines() == ["1", "100"]


# --- lists / indexing ---

def test_list_and_index(capsys):
    assert interpret('x = [10, 20, 30]\nfarjine(x[1])', capsys).strip() == "20"


def test_negative_index(capsys):
    assert interpret('x = [10, 20, 30]\nfarjine(x[-1])', capsys).strip() == "30"


# --- builtins parity ---

def test_range_and_len_builtins(capsys):
    assert interpret('farjine(len([1, 2, 3]))', capsys).strip() == "3"
    out = interpret('la x, range(3):\n    farjine(x)\n', capsys)
    assert out.splitlines() == ["0", "1", "2"]


# --- errors ---

def test_undefined_variable_raises_lebnene_error(capsys):
    with pytest.raises(LebneneError):
        interpret('farjine(y)', capsys)


def test_undefined_function_raises_lebnene_error(capsys):
    with pytest.raises(LebneneError):
        interpret('farjine(mystery(1))', capsys)


def test_wrong_arg_count_raises_lebnene_error(capsys):
    source = "3arref f(a, b):\n    redele a + b\nfarjine(f(1))\n"
    with pytest.raises(LebneneError):
        interpret(source, capsys)


# --- parity: interpreter output must match transpiler output on every example ---

EXAMPLE_FILES = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "examples", "*.lb")))


@pytest.mark.parametrize("path", EXAMPLE_FILES)
def test_interpreter_matches_transpiler_on_examples(path, capsys):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    transpiled_output = transpile_and_run(source, capsys)
    interpreted_output = interpret(source, capsys)
    assert interpreted_output == transpiled_output


# --- CLI wiring (--interpret flag) ---

def test_parse_args_defaults_to_transpile():
    from lebnene import parse_args
    assert parse_args(["script.lb"]) == ("transpile", "script.lb")


def test_parse_args_interpret_flag_with_script():
    from lebnene import parse_args
    assert parse_args(["--interpret", "script.lb"]) == ("interpret", "script.lb")
    assert parse_args(["script.lb", "--interpret"]) == ("interpret", "script.lb")


def test_parse_args_interpret_flag_repl_only():
    from lebnene import parse_args
    assert parse_args(["--interpret"]) == ("interpret", None)


def test_parse_args_no_args_is_repl():
    from lebnene import parse_args
    assert parse_args([]) == ("transpile", None)


def test_parse_args_too_many_positional_args_is_none():
    from lebnene import parse_args
    assert parse_args(["a.lb", "b.lb"]) is None


def test_main_exits_64_on_bad_args(monkeypatch):
    import lebnene
    monkeypatch.setattr("sys.argv", ["lebnene", "a.lb", "b.lb"])
    with pytest.raises(SystemExit) as exc_info:
        lebnene.main()
    assert exc_info.value.code == 64


def test_main_runs_a_script(monkeypatch, capsys, tmp_path):
    import lebnene
    script = tmp_path / "hi.lb"
    script.write_text('farjine("hi from main")', encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["lebnene", str(script)])
    lebnene.main()
    assert capsys.readouterr().out.strip() == "hi from main"


def test_run_interpret_mode_produces_output(capsys):
    from lebnene import run
    run('farjine("hi")', mode="interpret")
    assert capsys.readouterr().out.strip() == "hi"
