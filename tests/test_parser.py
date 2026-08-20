import pytest

from lexer import Lexer
from parser import Parser
from errors import LebneneError
from ast_nodes import (
    AssignStatement, PrintStatement, IfStatement, WhileStatement, ForStatement,
    FunctionDef, ReturnStatement, BinaryExpr, LiteralExpr, IdentifierExpr,
)


def parse(source):
    return Parser(Lexer(source).scan_tokens()).parse()


def test_assign_print_if_source_parses_to_expected_ast():
    source = '''x = 42
farjine("marhaba")
iza x == 42:
    farjine("sa7!")
'''
    statements = parse(source)
    assert len(statements) == 3

    assign, print_stmt, if_stmt = statements

    assert isinstance(assign, AssignStatement)
    assert assign.name == "x"
    assert assign.operator == "="
    assert isinstance(assign.value, LiteralExpr)
    assert assign.value.value == 42

    assert isinstance(print_stmt, PrintStatement)
    assert isinstance(print_stmt.expression, LiteralExpr)
    assert print_stmt.expression.value == "marhaba"

    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.condition, BinaryExpr)
    assert isinstance(if_stmt.condition.left, IdentifierExpr)
    assert if_stmt.condition.left.name == "x"
    assert if_stmt.condition.operator.lexeme == "=="
    assert if_stmt.condition.right.value == 42
    assert if_stmt.else_body is None
    assert len(if_stmt.body) == 1
    assert isinstance(if_stmt.body[0], PrintStatement)
    assert if_stmt.body[0].expression.value == "sa7!"


def test_while_loop_parses():
    statements = parse("talama x < 5:\n    x = x + 1\n")
    assert len(statements) == 1
    assert isinstance(statements[0], WhileStatement)
    assert len(statements[0].body) == 1
    assert isinstance(statements[0].body[0], AssignStatement)


def test_for_loop_parses():
    statements = parse("la x, [1, 2]:\n    farjine(x)\n")
    assert len(statements) == 1
    stmt = statements[0]
    assert isinstance(stmt, ForStatement)
    assert stmt.var_name == "x"


def test_function_def_and_return_parse():
    statements = parse("3arref jam3(a, b):\n    redele a + b\n")
    assert len(statements) == 1
    func = statements[0]
    assert isinstance(func, FunctionDef)
    assert func.name == "jam3"
    assert func.params == ["a", "b"]
    assert len(func.body) == 1
    assert isinstance(func.body[0], ReturnStatement)


def test_missing_closing_paren_raises():
    with pytest.raises(LebneneError):
        parse('farjine("hi"')
