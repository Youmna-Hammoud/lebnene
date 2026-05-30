# Lebnene 🇱🇧
A Lebanese programming language.

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
| talama   | while   | coming soon
| redele   | return  | coming soon
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
source.lb -> Lexer -> Parser -> Transpiler -> Python -> Output
```

## Status
- [x] Lexer
- [x] Parser
- [x] Python transpiler (MVP)
- [ ] Arithmetic operations
- [ ] While loops (talama)
- [ ] Functions (redele/return)
- [ ] Interpreter
- [ ] Arduino transpiler

## Based on
Crafting Interpreters by Robert Nystrom