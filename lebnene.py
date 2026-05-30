import sys
from lexer import Lexer
from parser import Parser
from transpiler import Transpiler

def run(source):
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    parser = Parser(tokens)
    statements = parser.parse()

    transpiler = Transpiler(statements)
    output = transpiler.transpile()

    exec(output, {"__builtins__": __builtins__, "print": lebnene_print})

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
        except Exception as e:
            print(f"Meshkle: {e}")

def lebnene_print(*args):
    output = []
    for arg in args:
        if arg is True:
            output.append("sa7")
        elif arg is False:
            output.append("ghalat")
        elif arg is None:
            output.append("mashi")
        else:
            output.append(str(arg))
    print(" ".join(output))

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python lebnene.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()