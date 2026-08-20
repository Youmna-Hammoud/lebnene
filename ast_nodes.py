class PrintStatement:
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"PrintStatement({self.expression})"

class IfStatement:
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body
    def __repr__(self):
        return f"IfStatement({self.condition}, {self.body}, {self.else_body})"

class AssignStatement:
    def __init__(self, name, value, operator="="):
        self.name = name
        self.value = value
        self.operator = operator
    def __repr__(self):
        return f"AssignStatement({self.name}, {self.operator}, {self.value})"

class BinaryExpr:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"BinaryExpr({self.left}, {self.operator.lexeme}, {self.right})"

class LiteralExpr:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"LiteralExpr({self.value})"

class IdentifierExpr:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"IdentifierExpr({self.name})"

class UnaryExpr:
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
    def __repr__(self):
        return f"UnaryExpr({self.operator.lexeme}, {self.operand})"

class ListExpr:
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"ListExpr({self.elements})"

class IndexExpr:
    def __init__(self, target, index):
        self.target = target
        self.index = index
    def __repr__(self):
        return f"IndexExpr({self.target}, {self.index})"

class ForStatement:
    def __init__(self, var_name, iterable, body):
        self.var_name = var_name
        self.iterable = iterable
        self.body = body        # list of statements
    def __repr__(self):
        return f"ForStatement({self.var_name}, {self.iterable}, {self.body})"
    
class WhileStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStatement({self.condition}, {self.body})"
    
class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body        # list of statements
    
    def __repr__(self):
        return f"FunctionDef({self.name}, {self.params}, {self.body})"

class CallExpr:
    def __init__(self, name, args):
        self.name = name 
        self.args = args        # list of expressions
    
    def __repr__(self):
        return f"CallExpr({self.name}, {self.args})"

class ReturnStatement:
    def __init__(self, value):
        self.value = value      # expression to return
    
    def __repr__(self):
        return f"ReturnStatement({self.value})"