import builtins

from ast_nodes import (
    PrintStatement, IfStatement, AssignStatement, WhileStatement, ForStatement,
    FunctionDef, ReturnStatement, BinaryExpr, UnaryExpr, LiteralExpr,
    IdentifierExpr, CallExpr, ListExpr, IndexExpr
)
from lexer import TokenType
from errors import LebneneError

# Same allowlist as the transpile-then-exec path's SAFE_BUILTINS (lebnene.py),
# kept in sync deliberately: both execution paths should expose the same
# language surface. Lebnene has no import/file-I/O/eval syntax of its own,
# so nothing beyond this small set is needed.
SAFE_BUILTINS = {
    name: getattr(builtins, name)
    for name in (
        "range", "len", "str", "int", "float", "bool",
        "abs", "min", "max", "sum", "round",
    )
}


def lebnene_print(*args):
    output = []
    for arg in args:
        if arg is True:
            output.append("sa7")
        elif arg is False:
            output.append("ghalat")
        elif arg is None:
            output.append("mashi")
        else:
            output.append(str(arg))
    print(" ".join(output))


class Return(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise LebneneError(f"'{name}' mish ma3rouf (undefined)")

    def set(self, name, value):
        # Always binds in *this* environment, mirroring Python's own scoping:
        # if/while/for don't get their own Environment (see execute_block),
        # so a plain assignment inside one already lands in the enclosing
        # function/global scope. Inside a function body, this creates a
        # local that shadows any same-named global, exactly like the
        # transpile-then-exec path (which is real Python `def`/`=`).
        self.values[name] = value


COMPOUND_OPS = {
    "+=": lambda a, b: a + b,
    "-=": lambda a, b: a - b,
    "*=": lambda a, b: a * b,
    "/=": lambda a, b: a / b,
}

BINARY_OPS = {
    TokenType.PLUS: lambda a, b: a + b,
    TokenType.MINUS: lambda a, b: a - b,
    TokenType.STAR: lambda a, b: a * b,
    TokenType.SLASH: lambda a, b: a / b,
    TokenType.MOD: lambda a, b: a % b,
    TokenType.EQUALS_EQUALS: lambda a, b: a == b,
    TokenType.MISH_EQUALS: lambda a, b: a != b,
    TokenType.GREATER: lambda a, b: a > b,
    TokenType.LESS: lambda a, b: a < b,
    TokenType.GREATER_EQUALS: lambda a, b: a >= b,
    TokenType.LESS_EQUALS: lambda a, b: a <= b,
}


class Interpreter:
    def __init__(self, statements, print_fn=lebnene_print):
        self.statements = statements
        self.print_fn = print_fn
        self.globals = Environment()
        self.functions = {}

    def run(self):
        self.execute_block(self.statements, self.globals)

    def execute_block(self, statements, env):
        for stmt in statements:
            self.execute(stmt, env)

    def execute(self, stmt, env):
        if isinstance(stmt, PrintStatement):
            self.print_fn(self.evaluate(stmt.expression, env))
        elif isinstance(stmt, AssignStatement):
            self.execute_assign(stmt, env)
        elif isinstance(stmt, IfStatement):
            if self.truthy(self.evaluate(stmt.condition, env)):
                self.execute_block(stmt.body, env)
            elif stmt.else_body is not None:
                self.execute_block(stmt.else_body, env)
        elif isinstance(stmt, WhileStatement):
            while self.truthy(self.evaluate(stmt.condition, env)):
                self.execute_block(stmt.body, env)
        elif isinstance(stmt, ForStatement):
            for item in self.evaluate(stmt.iterable, env):
                env.set(stmt.var_name, item)
                self.execute_block(stmt.body, env)
        elif isinstance(stmt, FunctionDef):
            self.functions[stmt.name] = stmt
        elif isinstance(stmt, ReturnStatement):
            raise Return(self.evaluate(stmt.value, env))
        else:
            raise LebneneError(f"Ma 3refet shou: {stmt}")

    def execute_assign(self, stmt, env):
        value = self.evaluate(stmt.value, env)
        if stmt.operator == "=":
            env.set(stmt.name, value)
            return
        current = env.get(stmt.name)
        env.set(stmt.name, COMPOUND_OPS[stmt.operator](current, value))

    def evaluate(self, expr, env):
        if isinstance(expr, LiteralExpr):
            return expr.value
        if isinstance(expr, IdentifierExpr):
            return env.get(expr.name)
        if isinstance(expr, ListExpr):
            return [self.evaluate(e, env) for e in expr.elements]
        if isinstance(expr, IndexExpr):
            return self.evaluate(expr.target, env)[self.evaluate(expr.index, env)]
        if isinstance(expr, UnaryExpr):
            return self.evaluate_unary(expr, env)
        if isinstance(expr, BinaryExpr):
            return self.evaluate_binary(expr, env)
        if isinstance(expr, CallExpr):
            return self.call(expr, env)
        raise LebneneError(f"Ma 3refet l expression: {expr}")

    def evaluate_unary(self, expr, env):
        operand = self.evaluate(expr.operand, env)
        if expr.operator.type == TokenType.MINUS:
            return -operand
        if expr.operator.type == TokenType.MISH:
            return not self.truthy(operand)
        raise LebneneError(f"Ma 3refet l operator: {expr.operator.lexeme}")

    def evaluate_binary(self, expr, env):
        op = expr.operator.type
        # short-circuit, matching Python's own and/or (the transpile target)
        if op == TokenType.AW:
            left = self.evaluate(expr.left, env)
            return left if self.truthy(left) else self.evaluate(expr.right, env)
        if op == TokenType.W:
            left = self.evaluate(expr.left, env)
            return self.evaluate(expr.right, env) if self.truthy(left) else left

        left = self.evaluate(expr.left, env)
        right = self.evaluate(expr.right, env)
        if op not in BINARY_OPS:
            raise LebneneError(f"Ma 3refet l operator: {expr.operator.lexeme}")
        return BINARY_OPS[op](left, right)

    def truthy(self, value):
        return bool(value)

    def call(self, expr, env):
        args = [self.evaluate(a, env) for a in expr.args]
        if expr.name in self.functions:
            return self.call_function(self.functions[expr.name], args)
        if expr.name in SAFE_BUILTINS:
            return SAFE_BUILTINS[expr.name](*args)
        raise LebneneError(f"'{expr.name}' mish ma3rouf (undefined function)")

    def call_function(self, func_def, args):
        if len(args) != len(func_def.params):
            raise LebneneError(
                f"{func_def.name}() badda {len(func_def.params)} arguments, "
                f"ejo {len(args)}"
            )
        call_env = Environment(self.globals)
        for name, value in zip(func_def.params, args):
            call_env.set(name, value)
        try:
            self.execute_block(func_def.body, call_env)
        except Return as r:
            return r.value
        return None
