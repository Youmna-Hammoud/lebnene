from lexer import Lexer

source = '''
3arref jam3(a, b):
    redele a + b

x = jam3(3, 4)
farjine(x)
'''

lexer = Lexer(source)
tokens = lexer.scan_tokens()

for token in tokens:
    print(token)