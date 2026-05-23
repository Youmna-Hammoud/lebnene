from lexer import Lexer

source = '''
x = 42
farjine("marhaba")
iza x == 42:
    farjine("sa7!")
'''

lexer = Lexer(source)
tokens = lexer.scan_tokens()
for token in tokens:
    print(token)