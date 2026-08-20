import sys
from lexer import Lexer
from parser import Parser
from transpiler import Transpiler
from interpreter import Interpreter, SAFE_BUILTINS, lebnene_print

def run(source, mode="transpile"):
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    if mode == "interpret":
        Interpreter(statements).run()
        return

    transpiler = Transpiler(statements)
    output = transpiler.transpile()

    exec(output, {"__builtins__": SAFE_BUILTINS, "print": lebnene_print})

def run_file(path, mode="transpile"):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    run(source, mode)

def repl_lines(read_line):
    """Yield complete source snippets from an interactive input source.

    A line ending in ':' opens a block; lines are buffered (REPL shows a
    '...' continuation prompt) until a blank line or EOF closes it, since a
    single input() line can never carry the NEWLINE+INDENT the parser needs
    for a block body.
    """
    buffer = []
    while True:
        prompt = "... " if buffer else "> "
        try:
            line = read_line(prompt)
        except EOFError:
            if buffer:
                yield "\n".join(buffer) + "\n"
            return

        if not buffer:
            if line.strip() == "":
                continue
            if line.rstrip().endswith(':'):
                buffer.append(line)
                continue
            yield line
        else:
            if line.strip() == "":
                yield "\n".join(buffer) + "\n"
                buffer = []
            else:
                buffer.append(line)

def run_prompt(mode="transpile"):
    print(f"Lebnene REPL ({mode})")
    for source in repl_lines(input):
        try:
            run(source, mode)
        except Exception as e:
            print(f"Meshkle: {e}")

def parse_args(argv):
    """argv excludes the script name (i.e. pass sys.argv[1:]).

    Returns (mode, path_or_None), or None if argv is malformed (too many
    positional arguments).
    """
    args = list(argv)
    mode = "transpile"
    if "--interpret" in args:
        mode = "interpret"
        args.remove("--interpret")
    if len(args) > 1:
        return None
    path = args[0] if args else None
    return mode, path

def main():
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        print("Usage: lebnene [--interpret] [script]")
        sys.exit(64)
    mode, path = parsed
    if path:
        run_file(path, mode)
    else:
        run_prompt(mode)

if __name__ == "__main__":
    main()