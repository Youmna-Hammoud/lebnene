# Lebnene — Roadmap / Future Tasks

Lebnene is at v0.1-mvp: lexer, parser, two interchangeable execution back
ends (transpile-then-`exec`, and a tree-walking interpreter via
`--interpret`), lists, functions, control flow, and a real test/CI/packaging
setup. This document lists what's left, grouped by what unlocks the most
value per effort. Each item was checked against the current code, not
proposed blind — see [TECHNICAL.md](TECHNICAL.md#known-limitations) for the
specific lines each bug references. **Current state: P0–P3 all done; the
Arduino backend is the only item left.**

## P0 — Correctness bugs (small, high-value) — DONE

Cheap fixes that close gaps between what looks supported and what actually
parses. Fixed with a real pytest suite (`tests/test_p0_fixes.py`, 10 tests)
written test-first; all example scripts re-run afterward with identical
output to confirm no regressions.

- [x] **Fix the standalone `!` lexer bug.** `scan_token` now calls
      `self.error(...)` for a bare `!` instead of `self.add_token(None)`,
      matching how every other unrecognized character is handled.
- [x] **Wire up `w` / `aw` / `mish` (and/or/not) in the parser.** Added
      `logic_or()` / `logic_and()` / `logic_not()` levels between
      `expression()` and `comparison()`, matching Python's `or`/`and`/`not`
      precedence (comparisons bind tighter than `mish`, `mish` binds tighter
      than `w`, `w` binds tighter than `aw`). A new `UnaryExpr` AST node
      carries `mish`; the transpiler maps `w`/`aw`/`mish` to Python's
      `and`/`or`/`not` via an explicit lookup table instead of reusing the
      raw lexeme. **Note:** this covers logical `mish` only — arithmetic
      unary minus (`x = -5`) is still unsupported, tracked below under P1.
- [x] **Add indentation-consistency validation.** `handle_indent` now raises
      `SyntaxError` if, after popping the dedent stack, the final `indent`
      doesn't exactly match the level it landed on.
- [x] **Count tabs in indentation.** `handle_indent` now advances over both
      `' '` and `'\t'` when measuring indent width.

## P1 — Core language completeness — DONE

Things a user will hit almost immediately once writing anything beyond the
example scripts. The mechanical items (no new keywords/syntax to invent) were
verified with a 20-test pytest suite (`tests/test_p1_fixes.py`). Collections
and `for` loops needed a naming/design decision — checked with the project
owner before implementing (`la` for "for", comma syntax over a reserved "in"
word, Python-style `[]` for lists) — then verified with an 11-test suite
(`tests/test_p1_collections.py`). All example scripts re-run after each
change to confirm no regressions; see `examples/lists.lb` for a demo of
lists, indexing, `la`, and `gherhek iza` together.

- [x] **`elif` support** — `gherhek iza` chains via recursion in
      `if_statement()` (no new keyword: `iza` immediately after `gherhek`
      triggers it). Transpiles to nested Python `else: if ...:` rather than
      flat `elif` — semantically identical, one extra indent level per branch.
- [x] **Unary minus** — `x = -5`, `farjine(5 - -3)` now parse via a new
      `unary()` precedence level between `multiplication` and `term`.
- [x] **String escapes** (`\n`, `\t`, `\"`, `\\`) via a lexer-level
      `unescape()` plus a transpiler switch from manual quote-wrapping to
      Python's `repr()` for string literals (fixes escaping generally, not
      just the four supported sequences). Concatenation via `+` already
      worked (Python's own `+` on the transpile target); no separate feature
      needed there.
- [x] **Compound assignment** (`+=`, `-=`, `*=`, `/=`) and **modulo** (`%`).
      `AssignStatement` gained an `operator` field (default `"="`); Python
      supports the same compound-assignment set natively so transpilation is
      direct.
- [x] **Comparison chaining `>=`, `<=`** — lexer now checks for a trailing
      `=` after `>`/`<` the same way it already did for `=`/`!`.
- [x] **Collection types (lists)** — `[1, 2, 3]` literals and `x[0]`
      indexing (Python-style, including negative and chained indexing like
      `x[0][1]`), via new `ListExpr`/`IndexExpr` AST nodes and a `primary()`/
      `term()` split in the parser (`term()` now parses one `primary` then
      loops on postfix `[...]`). Dicts/maps still not started — a stretch
      goal, not attempted this pass.
- [x] **`for` loops** — `la x, iterable:` (`ForStatement`), transpiling
      directly to Python's `for x in iterable:`. Deliberately uses a comma
      instead of an "in" keyword: a short word like `b` would have to become
      reserved, and `b` is already a real parameter name in the codebase's
      own test fixtures (`jam3(a, b)`) — reserving it would have silently
      broken that example. No `break`/`continue` yet for either `la` or
      `talama` — tracked as a gap in
      [TECHNICAL.md](TECHNICAL.md#known-limitations), not yet on this list
      as a task.

### P1 follow-ups (surfaced while building the above, not yet scheduled)

- [ ] **`break` / `continue`** for `la` and `talama` loops.
- [ ] **Index assignment** (`x[0] = 5`) — `assign_statement()` only accepts a
      bare identifier as a target today; extending it to accept an
      `IndexExpr` target would let list contents be mutated in place.
- [ ] **Dicts/maps** — the stretch part of the original collection-types
      item; not attempted this pass.

## P2 — Runtime & architecture

Bigger, more structural changes — worth sequencing after P0/P1 so they're not
built against a moving grammar. The three self-contained engineering items
are done, verified with a 15-test pytest suite (`tests/test_p2_fixes.py`).
The tree-walking interpreter and Arduino backend were genuinely large,
architecture-reshaping items — checked with the project owner before
starting either. The interpreter got a go-ahead (added alongside the
transpiler, not replacing it) and is done, verified with a 31-test suite
(`tests/test_interpreter.py`) including a parity check against every example
script. The Arduino backend is still deliberately on hold.

- [x] **Sandbox the `exec()` risk.** `run()` now passes a `SAFE_BUILTINS`
      dict (`range`, `len`, `str`, `int`, `float`, `bool`, `abs`, `min`,
      `max`, `sum`, `round` — the only builtin names generated code could
      plausibly need, since Lebnene has no import/file-I/O/eval syntax of
      its own) instead of the real `__builtins__`. Went with the stronger
      option rather than just documenting the risk, since checking the
      example scripts first confirmed none of them relied on any other
      builtin — `farjine(__import__("os"))` now raises `NameError` instead
      of actually importing a module.
- [x] **REPL multi-line input.** New `repl_lines()` generator in
      `lebnene.py`: a line ending in `:` opens a block (REPL shows a `...`
      continuation prompt); lines buffer until a blank line or EOF closes
      it, then the whole block is handed to `run()` as one source string.
      Pulled out as a pure generator (takes a `read_line(prompt)` callable)
      specifically so it's unit-testable without mocking real stdin.
- [x] **Consistent error types.** New `errors.py` with a single
      `LebneneError(SyntaxError)`. All *hard* failures — parser `expect()`
      and its other raise sites, the lexer's inconsistent-indentation check,
      the transpiler's two defensive fallback raises — now raise it instead
      of a mix of bare `SyntaxError` and generic `Exception`. It subclasses
      `SyntaxError` so existing `except SyntaxError` / `pytest.raises(SyntaxError)`
      call sites keep working unchanged. **Deliberately out of scope:** the
      lexer's *soft* error path (`self.error()`, used for an unrecognized
      character or an unterminated string) still just prints and lets
      scanning continue — converting that to a hard raise too would be a
      separate, bigger behavioral change (the lexer's current "keep going
      after a typo" leniency), not just a type-unification, so it's left as
      a distinct decision rather than folded in here.
- [x] **Tree-walking interpreter** (`interpreter.py`), added *alongside*
      transpile-then-`exec` rather than replacing it — `python lebnene.py
      --interpret script.lb` (or bare `--interpret` for the REPL). Same
      `jlox`-style dispatch shape as the transpiler
      (`isinstance()`-based `execute`/`evaluate`), operating on the AST
      directly with no intermediate Python text. `SAFE_BUILTINS` and
      `lebnene_print` moved into `interpreter.py` as the single shared
      definition both back ends import, rather than duplicating them.
      Verified two ways: 20 direct behavior tests, plus a parametrized parity
      test that runs every `examples/*.lb` file through both back ends and
      asserts identical stdout — new example scripts get this check for free.
      See [TECHNICAL.md](TECHNICAL.md#interpreter-interpreterpy) for the
      scoping/closures design (no closures; function-call environments
      parent directly to global scope, matching what the transpiled Python
      `def` bodies already do).
- [ ] **Arduino transpiler**, the other unchecked README box — a second
      backend alongside the Python one. Needs real design decisions (target
      C++ dialect, how Lebnene's dynamic types map onto a statically-typed
      embedded target, what happens to `farjine`/lists/functions on hardware
      with no stdout) that are out of scope to guess at. Held off deliberately
      after checking — not started this pass.

## P3 — Project hygiene (what "professional" mostly means here) — DONE

None of this touches the language itself, but it's what turns a single
`.py`-files-in-a-folder project into something a stranger — or you, in six
months — could pick up confidently.

- [x] **Convert `tests/` into real pytest test suites.** All three files
      rewritten with `def test_...()` functions and real `assert`s, in place
      of the old print-and-eyeball scripts — 16 tests total (7 lexer, 5
      parser, 4 transpiler), covering the same sample sources the originals
      used plus a few extra edge cases (keyword table sweep, missing-paren
      error). Confirmed the bare `pytest tests/` command (as CI runs it, not
      `python -m pytest`) actually collects them — see the `pythonpath`
      caveat under Packaging below.
- [x] **Packaging.** New [pyproject.toml](../pyproject.toml): `setuptools`
      backend, `lebnene = "lebnene:main"` console-script entry point (needed
      pulling the `if __name__ == "__main__":` body out into a real `main()`
      function first, since entry points need a callable, not a script
      block). Verified for real — installed into a throwaway venv with
      `pip install -e .` and ran the resulting `lebnene` command against
      example scripts in both execution modes before deleting the venv.
      **Caught along the way:** bare `pytest tests/` (unlike
      `python -m pytest`, which adds the current directory to `sys.path`
      automatically) couldn't import `lexer`/`parser`/etc. at all —
      `pythonpath = ["."]` under `[tool.pytest.ini_options]` fixes it. Worth
      knowing since the CI workflow below runs the bare form.
- [x] **CI** ([.github/workflows/tests.yml](../.github/workflows/tests.yml)).
      Runs `pytest tests/` plus every `examples/*.lb` script in both
      execution modes, on Python 3.9/3.10/3.11/3.12, on push/PR to `main`.
- [x] **`LICENSE` file.** MIT — checked with the project owner first (Apache
      2.0 and "no license" were the other options offered); copyright holder
      taken from the repo's own git commit author.
- [x] **Syntax highlighting** ([editors/vscode/](../editors/vscode/)). A
      TextMate grammar covering every keyword from the table in
      [TECHNICAL.md](TECHNICAL.md), strings with escapes, comments, numbers,
      and function names (both `3arref name` definitions and `name(...)`
      calls) — plus a `language-configuration.json` for bracket matching and
      indent-on-`:` behavior. Not published to the Marketplace; loaded
      locally via "Developer: Install Extension from Location...". All three
      JSON files validated with `json.load()` before committing.
- [x] **Keep the README/TECHNICAL/ROADMAP status checkboxes in sync.** Done
      as part of each change above, not as an afterthought — this bullet
      itself is now the record of that having happened for P0–P3.

## Suggested order

P0 is a few hours of focused work and removes real footguns (silent
mismatched indentation, a lexer bug, dead keywords) before anyone writes
more example programs against the current grammar. P1 is what makes example
programs stop feeling artificially limited. P2 is the architecturally
interesting part — sandboxing, error consistency, REPL blocks, and the
interpreter are now done; only the Arduino target remains, on hold pending a
dedicated design pass. P3 (real tests, packaging, CI, LICENSE, syntax
highlighting) is done too — it was independent of the language work above by
design, so it landed without waiting on P2. Only the Arduino backend is left
unstarted across the whole roadmap.
