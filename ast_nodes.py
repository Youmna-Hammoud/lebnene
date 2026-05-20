class PrintStatement:
    def __init__(self, expression):
        self.expression = expression

class IfStatement:
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

class AssignStatement:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class BinaryExpr:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class LiteralExpr:
    def __init__(self, value):
        self.value = value

class IdentifierExpr:
    def __init__(self, name):
        self.name = name