from lexer import Lexer
from parser import Parser

source = '''x = 42
farjine("marhaba")
iza x == 42:
    farjine("sa7!")
'''

lexer = Lexer(source)
tokens = lexer.scan_tokens()

parser = Parser(tokens)
statements = parser.parse()

for stmt in statements:
    print(stmt)