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
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f"AssignStatement({self.name}, {self.value})"

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