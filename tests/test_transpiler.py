from lexer import Lexer
from parser import Parser
from transpiler import Transpiler

source = '''x = 42
farjine("marhaba")
iza x == 42:
    farjine("sa7!")
'''

lexer = Lexer(source)
tokens = lexer.scan_tokens()
parser = Parser(tokens)
statements = parser.parse()
transpiler = Transpiler(statements)
output = transpiler.transpile()

print("=== Python output ===")
print(output)
print("=== Running it ===")
exec(output)