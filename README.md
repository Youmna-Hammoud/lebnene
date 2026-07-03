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
| gherhek  | else    |
| talama   | while   |
| 3arref   | def     |
| redele   | return  |
| sa7      | true    |
| ghalat   | false   |
| mashi    | null    |

## Usage

### Run a script
```bash
python lebnene.py marhaba.lb
```

### REPL
```bash
python lebnene.py
> farjine("marhaba")
marhaba
```
 
## How it works
```
source.lb -> Lexer -> Parser -> Transpiler -> Python -> Output (MVP)
```

## Status

Current MVP: v0.1-mvp

- [x] Lexer
- [x] Parser
- [x] Python transpiler (MVP)
- [x] Arithmetic operations
- [x] While loops (talama)
- [x] Functions (redele/return)
- [ ] Interpreter
- [ ] Arduino transpiler

## Based on
Crafting Interpreters by Robert Nystrom