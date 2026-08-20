from lexer import Lexer
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


# --- list literals ---

def test_list_literal_prints(capsys):
    assert run('farjine([1, 2, 3])', capsys).strip() == "[1, 2, 3]"


def test_empty_list_literal(capsys):
    assert run('farjine([])', capsys).strip() == "[]"


def test_list_of_strings(capsys):
    assert run('farjine(["a", "b"])', capsys).strip() == "['a', 'b']"


# --- indexing ---

def test_index_list_literal(capsys):
    assert run('farjine([10, 20, 30][1])', capsys).strip() == "20"


def test_index_variable(capsys):
    assert run('x = [10, 20, 30]\nfarjine(x[0])', capsys).strip() == "10"


def test_index_negative(capsys):
    assert run('x = [10, 20, 30]\nfarjine(x[-1])', capsys).strip() == "30"


def test_chained_index(capsys):
    assert run('x = [[1, 2], [3, 4]]\nfarjine(x[1][0])', capsys).strip() == "3"


# --- for loop ---

def test_for_loop_over_list_literal(capsys):
    source = 'la x, [1, 2, 3]:\n    farjine(x)\n'
    assert run(source, capsys).splitlines() == ["1", "2", "3"]


def test_for_loop_over_variable(capsys):
    source = 'items = [10, 20]\nla x, items:\n    farjine(x)\n'
    assert run(source, capsys).splitlines() == ["10", "20"]


def test_for_loop_body_can_accumulate(capsys):
    source = (
        'total = 0\n'
        'la x, [1, 2, 3, 4]:\n'
        '    total = total + x\n'
        'farjine(total)\n'
    )
    assert run(source, capsys).strip() == "10"


# --- regression: identifiers named 'b' still work (not reserved) ---

def test_identifier_named_b_still_works(capsys):
    source = (
        '3arref jam3(a, b):\n'
        '    redele a + b\n'
        'farjine(jam3(3, 4))\n'
    )
    assert run(source, capsys).strip() == "7"
