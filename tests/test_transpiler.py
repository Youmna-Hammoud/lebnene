from lexer import Lexer
from parser import Parser
from transpiler import Transpiler
from interpreter import SAFE_BUILTINS, lebnene_print


def transpile(source):
    statements = Parser(Lexer(source).scan_tokens()).parse()
    return Transpiler(statements).transpile()


def run_transpiled(source, capsys):
    output = transpile(source)
    exec(output, {"__builtins__": SAFE_BUILTINS, "print": lebnene_print})
    return capsys.readouterr().out


def test_assign_print_if_transpiles_to_valid_python():
    source = '''x = 42
farjine("marhaba")
iza x == 42:
    farjine("sa7!")
'''
    output = transpile(source)
    assert output == (
        "x = 42\n"
        "print('marhaba')\n"
        "if x == 42:\n"
        "    print('sa7!')"
    )


def test_assign_print_if_runs_and_prints_expected_output(capsys):
    source = '''x = 42
farjine("marhaba")
iza x == 42:
    farjine("sa7!")
'''
    out = run_transpiled(source, capsys)
    assert out.splitlines() == ["marhaba", "sa7!"]


def test_function_def_transpiles_and_runs(capsys):
    source = "3arref jam3(a, b):\n    redele a + b\nfarjine(jam3(3, 4))\n"
    out = run_transpiled(source, capsys)
    assert out.strip() == "7"


def test_booleans_transpile_to_python_and_print_as_lebnene_words(capsys):
    out = run_transpiled("farjine(sa7)\nfarjine(ghalat)\nfarjine(mashi)\n", capsys)
    assert out.splitlines() == ["sa7", "ghalat", "mashi"]
