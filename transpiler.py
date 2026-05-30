from ast_nodes import *

class Transpiler:
    def __init__(self, statements):
        self.statements = statements
        self.indent_level = 0
    
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
        raise Exception(f"Ma 3refet shou: {stmt}")
    
    def indent(self):
        return "    " * self.indent_level

    def transpile_print(self, stmt):
        expr = self.transpile_expression(stmt.expression)
        return f"{self.indent()}print({expr})"
    
    def transpile_assign(self, stmt):
        value = self.transpile_expression(stmt.value)
        return f"{self.indent()}{stmt.name} = {value}"
    
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
                return f'"{expr.value}"'
            if expr.value is True:
                return "True"
            if expr.value is False:
                return "False"
            if expr.value is None:
                return "None"
            if isinstance(expr.value, float) and expr.value.is_integer():
                return str(int(expr.value))
            return str(expr.value)
        
        if isinstance(expr, IdentifierExpr):
            return expr.name
        
        if isinstance(expr, BinaryExpr):
            left = self.transpile_expression(expr.left)
            right = self.transpile_expression(expr.right)
            return f"{left} {expr.operator.lexeme} {right}"
        
        raise Exception(f"Ma 3refet l expression: {expr}")