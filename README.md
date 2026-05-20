# Lebnene 🇱🇧
A Lebanese programming language.

## Keywords
| Lebanese | English |
|----------|---------|
| farjine  | print   |
| iza      | if      |
| gherhek  | else    |
| talama   | while   |
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
```

### Example script: marhaba.lb
```bash
farjine("marhaba!")
iza sa7:
farjine("kello tamem")
```
(the terminal will show tokens at this stage)

## Status
- [x] Lexer
- [x] Parser
- [ ] Python transpiler (MVP)
- [ ] Interpreter
- [ ] Arduino transpiler

## Based on
Crafting Interpreters by Robert Nystrom