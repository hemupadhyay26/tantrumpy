# tantrumpy

A zero-dependency Python package that intercepts app exit signals and fires a dramatic,
emotional, single-line message to the terminal before the process dies.
Zero configuration — one line to activate.

---

## Tech Stack

- **Language:** Python >= 3.8
- **Build system:** `hatchling` via `pyproject.toml`
- **Runtime dependencies:** None
- **Dev dependencies:** `pytest`, `pytest-cov`
- **Standard library only:** `signal`, `atexit`, `sys`, `os`, `random`

> See also: [development-best-practices.md](.claude/reference/development-best-practices.md) — type annotation rules, module responsibilities, code style

---

## Project File Structure

```
tantrumpy/
├── tantrumpy/
│   ├── __init__.py      # Public API: enable(), disable(), add_messages()
│   ├── handler.py       # TantrumHandler — signal/atexit/excepthook wiring
│   ├── messages.py      # Built-in mood message banks (6 moods × 15+ messages)
│   ├── picker.py        # Random message selection with no-repeat logic
│   └── colors.py        # ANSI color codes + supports_color() detection
├── examples/
│   └── demo.py          # Runnable demo for all moods and exit triggers
├── tests/
│   ├── test_handler.py
│   ├── test_messages.py
│   ├── test_picker.py
│   └── test_colors.py
├── .claude/
│   ├── PRD.md                              # Full Product Requirements Document
│   └── reference/
│       ├── development-best-practices.md   # Coding standards, patterns, type rules
│       └── testing-guide.md                # Test strategy, mocking patterns, examples
├── pyproject.toml
├── README.md
└── CLAUDE.md            # This file
```

---

## Logging

tantrumpy does **not** use Python's `logging` module internally.

- All output goes to `sys.stderr` — never `stdout`
- Output is suppressed entirely when `TANTRUMPY_SILENT=1` env var is set
- Colors are auto-disabled when stderr is not a TTY, `NO_COLOR` is set, or `TERM=dumb`
- No log files, no log levels — just one punchy line to stderr on exit

> See also: [development-best-practices.md](.claude/reference/development-best-practices.md#9-environment-variables) — full env var ownership table and error handling rules

---

## Testing Strategy

- **Framework:** `pytest`
- **Coverage:** `pytest-cov` (target >= 80%)
- **Scope:** Unit tests only for MVP — no integration tests requiring subprocess spawning
- **Signal testing:** Use `unittest.mock` to patch `signal.signal`, `atexit.register`, and `sys.excepthook` — do not send real OS signals in tests
- **No-repeat picker:** Verified by calling `pick()` N times and asserting no consecutive duplicates
- **Color fallback:** Verified by mocking `sys.stderr.isatty()` and env vars

### Key test rules
- Never call `sys.exit()` inside a test — mock it
- Never send real SIGINT/SIGTERM in tests — patch the handler
- Always reset `_fired` flag between test cases (use fixtures or monkeypatch)
- `TANTRUMPY_SILENT=1` must be tested to confirm zero output

> See also: [testing-guide.md](.claude/reference/testing-guide.md) — full mocking patterns, coverage targets, and test examples per module

---

## Test Organization

```
tests/
├── test_handler.py    # enable(), disable(), _fired guard, silent mode, verbose mode
├── test_messages.py   # Each mood has >= 15 messages, no empty strings, valid types
├── test_picker.py     # pick() returns valid message, no-repeat logic, random mood, custom moods
└── test_colors.py     # colorize() output, supports_color() fallback conditions
```

### Naming convention
- `test_<module>.py` maps 1-to-1 with `tantrumpy/<module>.py`
- Test functions: `test_<what>_<condition>` e.g. `test_enable_fires_on_sigint`, `test_pick_no_repeat`
- Fixtures in `conftest.py` if shared across files (e.g. reset handler state)

> See also: [testing-guide.md](.claude/reference/testing-guide.md#8-test-case-examples-by-module) — ready-to-use test examples for all 4 modules

---

## Reference Docs

Detailed guides live in `.claude/reference/`:

| File | Contents |
|------|----------|
| [`development-best-practices.md`](.claude/reference/development-best-practices.md) | Module responsibilities, type annotation rules, error handling, signal chaining, adding new moods |
| [`testing-guide.md`](.claude/reference/testing-guide.md) | Test stack, naming conventions, mocking patterns, coverage strategy, full examples per module |
