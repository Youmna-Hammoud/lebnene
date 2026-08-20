from ast_nodes import *
from lexer import TokenType
from errors import LebneneError

LOGICAL_OPERATORS = {
    TokenType.W: "and",
    TokenType.AW: "or",
    TokenType.MISH: "not",
}

class Transpiler:
    def __init__(self, statements):
        self.statements = statements
        self.indent_level = 0

    def transpile_operator(self, token):
        return LOGICAL_OPERATORS.get(token.type, token.lexeme)
    
    def transpile(self):
        lines=[]
        for stmt in self.statements:
            lines.append(self.transpile_statement(stmt))
        return "\n".join(lines)
    
    def transpile_statement(self, stmt):
        if isinstance(stmt, PrintStatement):
            return self.transpile_print(stmt)
        if isinstance(stmt, AssignStatement):
            return self.transpile_assign(stmt)
        if isinstance(stmt, IfStatement):
            return self.transpile_if(stmt)
        if isinstance(stmt, WhileStatement):
            return self.transpile_while(stmt)
        if isinstance(stmt, ForStatement):
            return self.transpile_for(stmt)
        if isinstance(stmt, FunctionDef):
            return self.transpile_function_def(stmt)
        if isinstance(stmt, ReturnStatement):
            return self.transpile_return(stmt)
        raise LebneneError(f"Ma 3refet shou: {stmt}")
    
    def indent(self):
        return "    " * self.indent_level

    def transpile_print(self, stmt):
        expr = self.transpile_expression(stmt.expression)
        return f"{self.indent()}print({expr})"
    
    def transpile_assign(self, stmt):
        value = self.transpile_expression(stmt.value)
        return f"{self.indent()}{stmt.name} {stmt.operator} {value}"
    
    def transpile_if(self, stmt):
        condition = self.transpile_expression(stmt.condition)
        lines = []
        
        lines.append(f"{self.indent()}if {condition}:")
        
        self.indent_level += 1
        for s in stmt.body:
            lines.append(self.transpile_statement(s))
        self.indent_level -= 1
        
        if stmt.else_body:
            lines.append(f"{self.indent()}else:")
            self.indent_level += 1
            for s in stmt.else_body:
                lines.append(self.transpile_statement(s))
            self.indent_level -= 1
        
        return "\n".join(lines)
    
    def transpile_expression(self, expr):
        if isinstance(expr, LiteralExpr):
            if isinstance(expr.value, str):
                return repr(expr.value)
            if expr.value is True:
                return "True"
            if expr.value is False:
                return "False"
            if expr.value is None:
                return "None"
            return str(expr.value)
        
        if isinstance(expr, IdentifierExpr):
            return expr.name
        
        if isinstance(expr, BinaryExpr):
            left = self.transpile_expression(expr.left)
            right = self.transpile_expression(expr.right)
            op = self.transpile_operator(expr.operator)
            return f"{left} {op} {right}"

        if isinstance(expr, UnaryExpr):
            operand = self.transpile_expression(expr.operand)
            op = self.transpile_operator(expr.operator)
            return f"{op} {operand}"

        if isinstance(expr, CallExpr):
            args = ", ".join(self.transpile_expression(a) for a in expr.args)
            return f"{expr.name}({args})"

        if isinstance(expr, ListExpr):
            elements = ", ".join(self.transpile_expression(e) for e in expr.elements)
            return f"[{elements}]"

        if isinstance(expr, IndexExpr):
            target = self.transpile_expression(expr.target)
            index = self.transpile_expression(expr.index)
            return f"{target}[{index}]"

        raise LebneneError(f"Ma 3refet l expression: {expr}")
    
    def transpile_while(self, stmt):
        condition = self.transpile_expression(stmt.condition)
        lines = []
        
        lines.append(f"{self.indent()}while {condition}:")
        
        self.indent_level += 1
        for s in stmt.body:
            lines.append(self.transpile_statement(s))
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def transpile_for(self, stmt):
        iterable = self.transpile_expression(stmt.iterable)
        lines = []

        lines.append(f"{self.indent()}for {stmt.var_name} in {iterable}:")

        self.indent_level += 1
        for s in stmt.body:
            lines.append(self.transpile_statement(s))
        self.indent_level -= 1

        return "\n".join(lines)

    def transpile_function_def(self, stmt):
        params = ", ".join(stmt.params)
        lines = []
        
        lines.append(f"{self.indent()}def {stmt.name}({params}):")
        
        self.indent_level += 1
        for s in stmt.body:
            lines.append(self.transpile_statement(s))
        self.indent_level -= 1
        
        return "\n".join(lines)

    def transpile_return(self, stmt):
        value = self.transpile_expression(stmt.value)
        return f"{self.indent()}return {value}"