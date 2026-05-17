import sys
from lexer import Lexer

def run(source):
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    for token in tokens:
        print(token)

def run_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    run(source)

def run_prompt():
    print("Lebnene REPL")
    while True:
        try:
            line = input("> ")
            run(line)
        except EOFError:
            break

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python lebnene.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()