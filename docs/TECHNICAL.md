# Lebnene — Technical Documentation

Lebnene is a small programming language with Lebanese-Arabic (Arabizi) syntax,
implemented in Python. `.lb` source shares a common Lexer → Parser → AST
front end, then runs through one of two interchangeable back ends: transpile
to Python and `exec()` it (the default), or walk the AST directly with a
tree-walking interpreter (`--interpret`). It exists to explore language
implementation — lexing, parsing, AST construction, code generation, and
evaluation — following the structure of *Crafting Interpreters* (Robert
Nystrom).

This document describes how the implementation actually works today (v0.1
MVP), not the intended end state — see [ROADMAP.md](ROADMAP.md) for what's
planned.

## Pipeline

```
                                        +--> Transpiler --> Python source --> exec()   (default)
source.lb --> Lexer --> [Token] --> Parser --> [Statement AST]
                                        +--> Interpreter --> Output                     (--interpret)
```

Both back ends consume the exact same AST — the front end (lexer, parser,
AST shape) has no notion of which back end will run it. The stages live in
these files:

| Stage | File | Input | Output |
|---|---|---|---|
| Lexer | [`lexer.py`](../lexer.py) | raw source string | list of `Token` |
| Parser | [`parser.py`](../parser.py) | list of `Token` | list of AST statement nodes |
| AST | [`ast_nodes.py`](../ast_nodes.py) | — | plain data classes used by parser/transpiler/interpreter |
| Transpiler | [`transpiler.py`](../transpiler.py) | AST statement list | Python source string |
| Interpreter | [`interpreter.py`](../interpreter.py) | AST statement list | side effects (`farjine` output), directly — no intermediate text |
| Entry point | [`lebnene.py`](../lebnene.py) | CLI args / stdin | wires the above together, picks a back end, runs the result |
| Errors | [`errors.py`](../errors.py) | — | `LebneneError`, the one exception type all stages above raise for hard failures |

## Lexer (`lexer.py`)

Hand-written, single-pass, character-at-a-time scanner (`Lexer.scan_token`),
modeled directly on the `jlox` scanner from *Crafting Interpreters*.

**Token types** (`TokenType` enum): literals (`RA2EM` = number, `KELME` =
string), keywords, symbols, and structural tokens `NEWLINE` / `INDENT` /
`DEDENT`.

**Keyword table:**

| Lebanese | English | Token |
|---|---|---|
| `farjine` | print | `FARJINE` |
| `iza` | if | `IZA` |
| `gherhek` | else | `GHER_HEK` |
| `talama` | while | `TALAMA` |
| `la` | for | `LA` |
| `3arref` | def (function) | `ARREF` |
| `redele` | return | `REDELE` |
| `sa7` | true | `SA7` |
| `ghalat` | false | `GHALAT` |
| `mashi` | null | `MASHI` |
| `w` | and | `W` |
| `aw` | or | `AW` |
| `mish` | not | `MISH` |

**Design decision — digit-prefixed identifiers.** `3arref` (function
definition) starts with a digit, which would normally be scanned as a number.
`scan_token` special-cases this: if a digit is immediately followed by a
letter or `_`, the whole thing is scanned as an identifier instead of a
number (`if self.peek().isalpha() or self.peek() == '_': self.identifier()`).
This is what lets `3arref` exist as a keyword at all — it is not a general
"numbers can have letters" feature, it only fires at the point a digit run
would otherwise start.

**Indentation.** Lebnene uses Python-style significant whitespace instead of
braces for blocks. `handle_indent()` runs after every `NEWLINE` token: it
counts leading spaces and tabs, compares against an `indent_stack`, and emits
`INDENT` when the count grows or one-or-more `DEDENT` when it shrinks. This
mirrors CPython's own tokenizer approach at a much simpler level. A dedent
that doesn't land exactly on a previously-pushed indent width raises
`SyntaxError` (e.g. mixing 2-space and 4-space indents inconsistently).

**Comments.** `//` to end of line only; no block comments.

**Strings.** Double-quoted, can span multiple physical lines. Supports
backslash escapes `\n`, `\t`, `\"`, `\\` — `string()` skips over an escaped
character pair while scanning so an escaped quote doesn't end the string
early, then a module-level `unescape()` function (near `KEYWORDS`) resolves
the escapes against an `ESCAPES` table once the raw text between the quotes
is known.

**Operators.** `+`, `-`, `*`, `/` each check for a trailing `=` to produce a
compound-assignment token (`+=`, `-=`, `*=`, `/=`); `/` checks for a second
`/` first (comment) before checking for `=`. `>` and `<` similarly check for
a trailing `=` to produce `>=` / `<=`. `%` (modulo) is single-character.

## Parser (`parser.py`)

Hand-written recursive-descent parser, one method per grammar rule, again
following the `jlox`/Pratt-adjacent structure from *Crafting Interpreters*.
Precedence is expressed by call order, not a precedence table.

**Statement grammar (informal EBNF):**

```
program     := statement* EOF
statement   := printStmt | ifStmt | whileStmt | forStmt | funcDef | returnStmt | assignStmt

printStmt   := "farjine" "(" expression ")"
ifStmt      := "iza" expression ":" block ( "gherhek" ( "iza" ifStmt | ":" block ) )?
whileStmt   := "talama" expression ":" block
forStmt     := "la" IDENTIFIER "," expression ":" block
funcDef     := "3arref" IDENTIFIER "(" params? ")" ":" block
returnStmt  := "redele" expression
assignStmt  := IDENTIFIER ( "=" | "+=" | "-=" | "*=" | "/=" ) expression

block       := NEWLINE INDENT statement* DEDENT
params      := IDENTIFIER ( "," IDENTIFIER )*
```

`forStmt` uses a comma, not an "in" keyword (`la x, ra2am:`, not `la x b
ra2am:`), a deliberate choice: a single-letter word like `b` ("in") would
have to become reserved, and `b` is already a real parameter name in the
codebase's own test fixtures (`3arref jam3(a, b): redele a + b`) — reserving
it would silently break that example. The comma sidesteps the collision
entirely. `la`'s dedicated iteration variable is written directly into the
generated Python `for` loop, so it's an ordinary Python variable afterward
(no separate scoping mechanism).

`gherhek iza ...` ("elif") is not a separate grammar production or keyword —
`if_statement()` just checks whether `iza` immediately follows `gherhek` and,
if so, recursively calls itself and wraps the result as the sole statement in
`else_body`. This transpiles to a nested Python `else: if ...:` rather than a
flat `elif`, which is semantically identical but adds one indent level per
chained branch.

**Expression grammar (lowest to highest precedence):**

```
expression   := logic_or
logic_or     := logic_and ( "aw" logic_and )*
logic_and    := logic_not ( "w" logic_not )*
logic_not    := "mish" logic_not | comparison
comparison   := addition ( ( "==" | "!=" | ">" | "<" | ">=" | "<=" ) addition )*
addition     := multiplication ( ( "+" | "-" ) multiplication )*
multiplication := unary ( ( "*" | "/" | "%" ) unary )*
unary        := "-" unary | term
term         := primary ( "[" expression "]" )*     // postfix indexing, chainable
primary      := NUMBER | STRING | "sa7" | "ghalat" | "mashi"
              | "[" ( expression ( "," expression )* )? "]"    // list literal
              | IDENTIFIER ( "(" args? ")" )?      // bare identifier or call
args         := expression ( "," expression )*
```

`term` parses one `primary` and then loops on `[...]` for postfix indexing,
so `x[0]`, `[1, 2, 3][0]`, and `x[0][1]` (chained indexing) all fall out of
the same loop without special-casing which kind of primary precedes the
brackets. A leading `[` inside `primary` is unambiguous with the postfix use
because `primary` only ever runs once per `term`, at the position a value is
expected — by the time the postfix loop's own `[` check runs, that first
`primary` has already been consumed.

Every binary comparison/arithmetic/logical level is left-associative (`while`
loop building a left-leaning tree), matching standard operator semantics.
`logic_not` and `unary` are both right-associative (so `mish mish sa7` and
`- -5` both parse, recursing into themselves). `logic_not` binds tighter than
`w`/`aw` but looser than comparisons — same precedence ordering as Python's
`not`/`and`/`or`, so `mish sa7 w ghalat` parses as `(mish sa7) w ghalat`, not
`mish (sa7 w ghalat)`. `unary` sits between `multiplication` and `term`, so
`-` only starts a new term at the point one is expected (`5 - 3` still parses
as subtraction, not `5` followed by an invalid unary `-3`) — the `-` token is
shared between `addition`'s binary loop and `unary`'s prefix check with no
ambiguity, since by the time `unary` runs for an operand, any binary `-` has
already been consumed by the level above it. `w`/`aw`/`mish` transpile via an
explicit `LOGICAL_OPERATORS` lookup (`transpile_operator`) in the transpiler
rather than reusing the token's raw lexeme directly; arithmetic/comparison
operator lexemes (`+`, `-` — including unary `-` — `%`, `>=`, etc.) are
already valid Python syntax, so the same lookup just falls back to the
lexeme for those.

**Errors** raise `LebneneError` (from [`errors.py`](../errors.py), a thin
`SyntaxError` subclass — so existing `except SyntaxError` handling still
works unchanged) with the offending line number and an Arabizi message (e.g.
`"Lezem ')' ba3d l expression"` — "need ')' after the expression"). There is
no error recovery: the parser stops at the first failure.

## AST (`ast_nodes.py`)

Plain Python classes, no base class, no visitor pattern — the transpiler
dispatches on `isinstance()` instead. Each node stores its children as plain
attributes and defines `__repr__` for debugging (used directly by the
`tests/` smoke scripts, which print AST trees rather than asserting on them).

Nodes: `PrintStatement`, `IfStatement`, `AssignStatement`, `WhileStatement`,
`ForStatement`, `FunctionDef`, `ReturnStatement`, `BinaryExpr`, `UnaryExpr`,
`ListExpr`, `IndexExpr`, `LiteralExpr`, `IdentifierExpr`, `CallExpr`.

## Transpiler (`transpiler.py`)

Walks the AST once and emits Python source as a plain string, indenting with
4 spaces per level via an internal `indent_level` counter. Dispatch is a
chain of `isinstance()` checks in `transpile_statement` /
`transpile_expression` (`O(n)` per node in the number of node types — fine at
this scale, would want a dispatch dict or visitor if the node count grows).

Notable mappings:
- `sa7` / `ghalat` / `mashi` literals → Python `True` / `False` / `None`.
- String literals transpile via Python's own `repr()` rather than manual
  quote-wrapping, so escapes the lexer already resolved (`\n`, `\t`, etc.)
  come back out as a syntactically valid, correctly re-escaped Python string
  literal regardless of what characters the string contains.
- Most binary/unary operators transpile 1:1 by reusing the original token's
  `lexeme` (`==`, `!=`, `>`, `<`, `>=`, `<=`, `+`, `-`, `*`, `/`, `%` are
  valid Python operators too). `w`/`aw`/`mish` are the exception — their
  lexemes aren't Python syntax, so `transpile_operator()` maps them through
  `LOGICAL_OPERATORS` to `and`/`or`/`not` first; every other operator falls
  through that same lookup to its own lexeme.
- Compound assignment (`AssignStatement.operator`, one of `=`/`+=`/`-=`/
  `*=`/`/=`) transpiles directly, since Python supports the same set natively.
- `ListExpr` → a Python list literal; `IndexExpr` → Python `[]` subscript.
  Both transpile directly since Lebnene lists are just Python lists under
  the hood — no wrapper type, no bounds-checking beyond what Python itself
  raises.
- `la x, iterable:` (`ForStatement`) → Python `for x in iterable:`, with the
  loop variable written straight into the target `for` clause.
- Function defs, if/else (including chained `gherhek iza`), and while all
  transpile to their direct Python equivalent with a nested indent level.

## Interpreter (`interpreter.py`)

A tree-walking evaluator, `jlox`'s `Interpreter` class from *Crafting
Interpreters* translated to Python: `Interpreter.execute(stmt, env)` and
`.evaluate(expr, env)` dispatch on AST node type via `isinstance()`
(mirroring the transpiler's dispatch style) and act on the node directly —
no intermediate Python text, no `exec()`.

**Scoping (`Environment`).** One `Environment` (a `dict` plus a `parent`
link) per function call frame, plus one for the global/top-level scope.
`if`/`while`/`for` do **not** get their own `Environment` — they execute
directly against whatever environment they were called with — which is
deliberate: Python's own `if`/`while`/`for` don't introduce a new scope
either, so this keeps interpreter scoping identical to what the transpiled
Python code actually does. Concretely: `Environment.get()` walks up the
parent chain (so a function body can read a global), but `Environment.set()`
always writes into the *current* environment only, never walking up — so
assigning inside a function body creates/updates a local that shadows a
same-named global rather than mutating it, exactly like a real Python `def`
body would (see `test_function_local_scope_does_not_leak` in
`tests/test_interpreter.py`).

**Functions.** `FunctionDef` statements register into `self.functions` (a
name → `FunctionDef` dict) rather than executing anything; a `CallExpr`
looks the name up there first, then falls back to `SAFE_BUILTINS` (same
allowlist as the transpile path, defined once in `interpreter.py` and
imported by `lebnene.py` rather than duplicated). A call creates a new
`Environment` parented to `self.globals` (not to the caller's frame — Lebnene
has no closures, so every function call frame's parent is always the global
scope), binds params positionally, and executes the body; `redele`
(`ReturnStatement`) is implemented by raising a `Return(value)` exception
that `call_function()` catches, mirroring `jlox`'s own control-flow-via-
exception approach for early return from arbitrary nesting depth.

**Operator evaluation.** `w`/`aw` short-circuit exactly like Python's
`and`/`or` (evaluate left; only evaluate right if needed; return whichever
operand decided it, not a coerced bool) since that's what the transpiled
code's real Python `and`/`or` does — needed for behavioral parity between
the two back ends, not just "close enough". Arithmetic/comparison operators
go through a `BINARY_OPS` dispatch dict keyed on `TokenType`, each a small
lambda over real Python operators (so `/` is Python's true division, `%` is
Python's modulo, etc.) — same semantics as what the transpiler generates
literally as Python source, just invoked directly instead of via generated
text.

**Parity testing.** `tests/test_interpreter.py` runs every file in
`examples/` through both back ends and asserts identical stdout
(`test_interpreter_matches_transpiler_on_examples`, parametrized over
`examples/*.lb`) — the primary guard against the two back ends silently
drifting apart as the language grows.

## Runtime (`lebnene.py`)

`run(source, mode="transpile")` chains Lexer → Parser, then either hands the
AST to `Interpreter` (`mode="interpret"`) or continues to the Transpiler and
calls:

```python
exec(output, {"__builtins__": SAFE_BUILTINS, "print": lebnene_print})
```

`SAFE_BUILTINS` is an explicit allowlist (`range`, `len`, `str`, `int`,
`float`, `bool`, `abs`, `min`, `max`, `sum`, `round`) built from Python's
`builtins` module, rather than the real `__builtins__` passed straight
through. It lives in `interpreter.py` (not `lebnene.py`) and is imported
from there, so both back ends share exactly one definition rather than
risking two allowlists drifting apart. Since Lebnene has no import/file-I/O/
eval syntax of its own, generated code has no legitimate reason to reach
`__import__`, `open`, `eval`, etc. — a script that tries (e.g.
`farjine(__import__("os"))`, reachable because any bare identifier followed
by `(` transpiles to a direct Python call) now gets a `NameError` instead of
actually importing a module. `range` is included deliberately so
`la x, range(5):` works as an idiomatic counted loop.

`lebnene_print` (also defined once in `interpreter.py`, imported by
`lebnene.py`, and used as the interpreter's default `print_fn`) is a shim so
that Python's native `True`/`False`/`None` — the values `sa7`/`ghalat`/
`mashi` transpile to, and the actual Python booleans/`None` the interpreter
evaluates expressions to — print back out as `sa7`/`ghalat`/`mashi` rather
than Python's own spelling, identically on both back ends. This only
intercepts *printing*; internally, booleans and null remain ordinary Python
`True` / `False` / `None` either way.

**CLI modes** (`if __name__ == "__main__"`, parsed by `parse_args(argv)` —
pulled out as its own function specifically so argument parsing is
unit-testable without touching `sys.argv`):
- `python lebnene.py script.lb` → `run_file`, transpile-and-exec one file.
- `python lebnene.py --interpret script.lb` → same file, tree-walking
  interpreter instead.
- `python lebnene.py` / `python lebnene.py --interpret` (no script) →
  `run_prompt`, a REPL in the corresponding mode.
- More than one positional argument → usage message, exit code 64.

**REPL multi-line blocks.** `run_prompt` drives a `repl_lines()` generator
rather than calling `run()` on every raw `input()` line: a line ending in
`:` opens a block (the prompt switches to `...`), subsequent lines buffer
until a blank line or EOF closes it, and the buffered block is joined into
one source string and handed to `run()` as a unit. This exists because a
single `input()` line can never carry the `NEWLINE` + `INDENT` tokens the
parser requires for a block body. `repl_lines()` takes a `read_line(prompt)`
callable rather than calling `input()` directly, specifically so it can be
unit-tested with a fake line source instead of mocking stdin.

REPL exceptions are caught and printed as `Meshkle: {e}` ("problem: …")
rather than crashing the loop.

## Known limitations

These are gaps observed directly in the current implementation, not
speculative — each is a concrete line of code, not a guess. The P0 items
(dead `w`/`aw`/`mish` tokens, the standalone-`!` lexer bug, unvalidated
dedents, tabs not counted), all of P1 (unary minus, `elif`, `>=`/`<=`,
modulo, compound assignment, string escapes, lists, indexing, `la` for-loops),
and four P2 items (exec sandboxing, REPL multi-line input, consistent error
types, and a tree-walking interpreter as an additive second execution path)
tracked in [ROADMAP.md](ROADMAP.md) have been fixed. What remains:

- **No string interpolation.** Escapes (`\n`, `\t`, `\"`, `\\`) work, but
  there's no `"x is {x}"`-style templating — concatenation is the only way
  to build a string from parts, via `+` (which relies on Python's own `+`
  operator at the transpile target, so `"x is " + x` only works if `x` is
  already a string; there is no implicit str() coercion).
- **Lists have no methods.** No `.append`, `.length`, slicing, or `mish b`
  ("not in") style membership check — creation (`[1, 2, 3]`) and indexing
  (`x[0]`, negative indices, chained) are the only supported operations.
  Mutation via index assignment (`x[0] = 5`) also isn't wired up — only plain
  identifiers are valid assignment targets in `assign_statement()`.
- **No dicts/maps.** Lists are the only collection type.
- **No `break`/`continue`.** Neither `la` nor `talama` loops can be exited
  or skipped early from inside the body.
- **The lexer's *soft* error path is still lenient by design.** An
  unrecognized character or an unterminated string still goes through
  `self.error()`, which prints a message and lets scanning continue, rather
  than raising `LebneneError` like every other failure now does. This is
  deliberate, not an oversight missed during the P2 error-type cleanup —
  making it hard-fail too is a separate behavioral change (see
  [ROADMAP.md](ROADMAP.md)), not just a type-consistency fix.
- **No source of truth for what's implemented lives outside code + README.**
  This document and the README checklist are the only two places tracking
  feature status — keep both updated together as the language grows.
- **The interpreter has no closures.** Every function call's `Environment`
  parents directly to the global scope (`interpreter.py`'s
  `call_function()`), not to whatever scope the call happened in — matching
  the transpile path (real Python `def` bodies close over module globals,
  not over some enclosing call frame, since Lebnene has no nested function
  definitions yet either). Not a gap versus the transpiler, just a shared
  limitation of both back ends.
- **Still no non-Python compilation target.** An Arduino/C backend, listed
  in [ROADMAP.md](ROADMAP.md), hasn't been started — both current back ends
  ultimately run on the machine executing Python.

## Testing

105 tests across eight files under `tests/`, all real pytest suites now (see
[ROADMAP.md](ROADMAP.md) — converting the original three print-based smoke
scripts was a P3 item):

| File | Tests | Covers |
|---|---:|---|
| `test_lexer.py` | 7 | token sequences, literals, every keyword in `KEYWORDS` |
| `test_parser.py` | 5 | AST shape for assign/print/if, while, for, function+return, a parse error |
| `test_transpiler.py` | 4 | generated Python text, and running it end-to-end |
| `test_p0_fixes.py` | 10 | the `!` lexer bug, `w`/`aw`/`mish` parsing+precedence, indentation validation |
| `test_p1_fixes.py` | 20 | `elif`, unary minus, `>=`/`<=`, modulo, compound assignment, string escapes |
| `test_p1_collections.py` | 11 | list literals, indexing (negative, chained), `la` for-loops |
| `test_p2_fixes.py` | 15 | restricted `exec()` builtins, `LebneneError` consistency, REPL buffering |
| `test_interpreter.py` | 33 | interpreter behavior + CLI wiring (`parse_args`, `main()`) |

Each new behavior generally has a "still works" test alongside it (e.g.
`test_greater_still_works`, `test_identifier_named_b_still_works` — the
latter confirms that adding `la` as a keyword didn't break `b` as an
ordinary identifier) as a regression guard. `test_p2_fixes.py`'s REPL tests
drive the pure `repl_lines()` generator with a fake `read_line` callable
rather than mocking stdin. `test_interpreter.py` includes a parametrized
parity check (`test_interpreter_matches_transpiler_on_examples`) that runs
every file in `examples/` through both back ends and asserts identical
stdout — new example scripts get this coverage automatically, no test-file
edit needed.

Run with `pytest tests/` (or `python -m pytest tests/` — both now behave
identically; see the `pythonpath` note under
[Packaging & tooling](#packaging--tooling) for why that wasn't always true).

## Packaging & tooling

- **[pyproject.toml](../pyproject.toml)** — `setuptools` build backend, a
  `lebnene = "lebnene:main"` console-script entry point (which is why
  `lebnene.py`'s CLI dispatch lives in a real `main()` function rather than
  directly under `if __name__ == "__main__":` — entry points need a callable
  to import, not a script body), and `[tool.pytest.ini_options]`.
- **The `pythonpath` gotcha.** `python -m pytest` implicitly adds the current
  directory to `sys.path` (how `python -m` works generally), so
  `from lexer import Lexer` etc. resolved in every test file even before
  this file existed. Plain `pytest tests/` — what CI actually runs — does
  **not** get that for free; without `pythonpath = ["."]` under
  `[tool.pytest.ini_options]`, every test file fails to import with
  `ModuleNotFoundError: No module named 'lexer'`. Caught by literally running
  the CI command locally before trusting it, rather than assuming
  `python -m pytest` and `pytest` behave the same.
- **[.github/workflows/tests.yml](../.github/workflows/tests.yml)** — runs
  `pytest tests/`, then every `examples/*.lb` script in both execution
  modes, across Python 3.9–3.12, on push/PR to `main`.
- **[LICENSE](../LICENSE)** — MIT.
- **[editors/vscode/](../editors/vscode/)** — a TextMate grammar
  (`syntaxes/lebnene.tmLanguage.json`) plus `language-configuration.json`,
  covering every keyword in the table above, strings with escapes, comments,
  numbers, `3arref name` definitions, and `name(...)` calls. Not published to
  the Marketplace — load locally via "Developer: Install Extension from
  Location...". All three JSON files are validated with `json.load()` rather
  than trusted by eye.

## Running it

```bash
python lebnene.py examples/marhaba.lb              # run a script (transpiler, default)
python lebnene.py --interpret examples/marhaba.lb  # same script, tree-walking interpreter
python lebnene.py                                  # start the REPL
lebnene examples/marhaba.lb                         # same, if `pip install -e .` was run
pytest tests/                                       # run the full test suite
```

No runtime dependencies — standard library only (`sys`, `enum`, `builtins`).
`pytest` is the only dev-time dependency, for the test suite.
