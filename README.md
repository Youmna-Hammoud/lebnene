# Lebnene 🇱🇧
An educational programming language with Lebanese Arabic syntax.

Lebnene is a programming language implemented in Python to explore language design through lexing, parsing, AST construction, and interpretation.

## Example
```lb
x = 42
farjine("marhaba!")
 
iza x == 42:
    farjine("sa7, x betsewe 42!")
gherhek:
    farjine("mish 42")
```
 
Output:
```
marhaba!
sa7, x betsewe 42!
```

## Keywords
| Lebanese | English |
|----------|---------|
| farjine  | print   |
| iza      | if      |
| gherhek iza | elif |
| gherhek  | else    |
| talama   | while   |
| la       | for     |
| 3arref   | def     |
| redele   | return  |
| sa7      | true    |
| ghalat   | false   |
| mashi    | null    |
| w        | and     |
| aw       | or      |
| mish     | not     |

Lists use `[1, 2, 3]` / `x[0]` (Python-style); `for` loops read
`la x, iterable:`.

## Install

```bash
pip install -e .
```

This gives you a `lebnene` command (see [pyproject.toml](pyproject.toml)) —
everything below also works as `python lebnene.py ...` without installing.

## Usage

### Run a script
```bash
python lebnene.py marhaba.lb
# or, if installed:
lebnene marhaba.lb
```

### REPL
```bash
python lebnene.py
> farjine("marhaba")
marhaba
```

Blocks work at the REPL too — a line ending in `:` opens a `...` continuation
prompt; a blank line runs the buffered block:
```
> iza sa7:
...     farjine("yes")
...
yes
```

### Interpreter mode
Add `--interpret` to run via a tree-walking interpreter instead of
transpiling to Python and calling `exec()` — works with a script or the REPL:
```bash
python lebnene.py --interpret marhaba.lb
python lebnene.py --interpret
```
Both execution paths are kept in sync (`tests/test_interpreter.py` checks
every example script produces identical output either way); the transpiler
stays the default.

## How it works
```
                                  +--> Transpiler --> Python --> exec()   (default)
source.lb -> Lexer -> Parser --> |
                                  +--> Interpreter --> Output              (--interpret)
```

## Status

Current MVP: v0.1-mvp

- [x] Lexer
- [x] Parser
- [x] Python transpiler (MVP)
- [x] Arithmetic operations (`+ - * / %`, unary `-`)
- [x] While loops (talama) and for loops (la)
- [x] Functions (redele/return)
- [x] elif (gherhek iza), logical and/or/not (w/aw/mish)
- [x] Lists and indexing (`[1, 2, 3]`, `x[0]`)
- [x] Compound assignment (`+= -= *= /=`), string escapes
- [x] Interpreter (`--interpret`, alongside the transpiler)
- [ ] Arduino transpiler

## Development

```bash
pytest tests/        # run the test suite (105 tests)
```

CI ([.github/workflows/tests.yml](.github/workflows/tests.yml)) runs this
plus every `examples/*.lb` script, in both execution modes, on Python
3.9–3.12 on every push/PR to `main`.

## Editor support

[editors/vscode/](editors/vscode/) has `.lb` syntax highlighting for VS Code
(keywords, strings, comments, numbers, function names). Not published to the
Marketplace — load it locally via VS Code's "Developer: Install Extension
from Location..." command, pointing at the `editors/vscode/` folder.

## Documentation

- [docs/TECHNICAL.md](docs/TECHNICAL.md) — how the lexer, parser, AST, and
  transpiler actually work, plus known limitations found in the code.
- [docs/ROADMAP.md](docs/ROADMAP.md) — prioritized list of bugs, missing
  language features, and project-hygiene tasks still to do.

## License
[MIT](LICENSE)

## Based on
Crafting Interpreters by Robert Nystrom