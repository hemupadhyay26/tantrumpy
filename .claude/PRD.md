# tantrumpy — Product Requirements Document

---

## 1. Executive Summary

**tantrumpy** is a zero-dependency Python package that intercepts application exit signals and fires a dramatic, emotional, single-line message to the terminal before the process dies. It is designed to bring personality and humor to the otherwise silent and forgettable death of a Python process.

The core value proposition is simple: every Python app exits — most do it silently and without dignity. tantrumpy gives your app a voice in its final moment. Whether it's frustrated, rude, philosophical, or utterly cringe, the tantrum is always appropriate and always funny.

**MVP Goal:** Ship a pip-installable Python package (`pip install tantrumpy`) that any developer can drop into any project with a single line — `tantrumpy.enable()` — and have their app immediately start throwing exit tantrums. Zero configuration required, zero runtime dependencies.

---

## 2. Mission

**Make every Python app's death memorable.**

### Core Principles

1. **Zero friction** — One line to activate. No config files, no setup, no dependencies.
2. **Never block the exit** — tantrumpy adds personality, it never interferes with normal program flow.
3. **Works everywhere** — Graceful fallback for CI, piped output, dumb terminals, and Windows.
4. **Extensible by default** — Built-in moods cover 90% of use cases; custom moods for the rest.
5. **Opinionated but flexible** — Sane defaults out of the box, opt-in configuration when needed.

---

## 3. Target Users

### Primary Persona: The Developer Who Gets It
- Python developers (beginner to senior) who appreciate dark humor and personality in their tooling
- Works on CLI tools, scripts, web servers, data pipelines — anything that runs and exits
- Wants something that "just works" with no research required

### Secondary Persona: The Open Source Contributor
- Wants to add custom moods or contribute new message packs
- Comfortable with Python packaging and contributing to GitHub

### Technical Comfort Level
- Primary users: intermediate Python (knows `pip install`, imports, basic scripting)
- Package is approachable enough for beginners, flexible enough for power users

### Key User Needs
- Add personality to dev tools and CLI apps without writing boilerplate
- Surprise and delight collaborators or themselves during long dev sessions
- Customizable enough to fit their project's voice

---

## 4. MVP Scope

### Core Functionality
- ✅ `tantrumpy.enable()` — one-line activation with random mood
- ✅ `tantrumpy.enable(mood="frustrated")` — specific mood selection
- ✅ `tantrumpy.enable(verbose=True)` — include exit trigger context in message
- ✅ `tantrumpy.disable()` — unhook all handlers cleanly
- ✅ `tantrumpy.add_messages(mood, messages)` — register custom mood messages
- ✅ Hook: SIGINT (Ctrl+C)
- ✅ Hook: SIGTERM (kill signal)
- ✅ Hook: `sys.exit()` / normal script end (via `atexit`)
- ✅ Hook: Unhandled exceptions / crashes (via `sys.excepthook`)
- ✅ 6 built-in moods: `frustrated`, `rude`, `comic`, `cringe`, `philosophy`, `dramatic`
- ✅ 15+ messages per mood
- ✅ No-repeat picker (shuffle + rotate within session)
- ✅ Mood emoji prefix per message
- ✅ ANSI colored output (mood-based colors, colored by default)
- ✅ Smart color fallback (plain text when terminal doesn't support color)
- ✅ `TANTRUMPY_SILENT=1` env var for CI/prod suppression

### Technical
- ✅ Python >= 3.8 support
- ✅ Zero runtime dependencies
- ✅ Prints to `stderr` (never pollutes `stdout`)
- ✅ `pyproject.toml` build config (hatchling or setuptools)
- ✅ `pip install tantrumpy` installable

### Out of Scope (v1)
- ❌ Multi-line rant mode (deferred to v2)
- ❌ Logging framework integration (`logging.Handler` subclass)
- ❌ File output / log file support
- ❌ Web framework middleware (Flask, FastAPI, Django)
- ❌ Async/await support (asyncio signal handling)
- ❌ Windows ANSI auto-enable via `colorama`
- ❌ Plugin/extension system
- ❌ GUI/TUI display modes
- ❌ PyPI stats dashboard or telemetry

---

## 5. User Stories

**Story 1 — Zero-config activation**
> As a developer, I want to drop one line into my script and have it throw a tantrum on exit, so that I don't have to configure anything.

```python
import tantrumpy
tantrumpy.enable()
# ... rest of my app
```
Exit output: `😤 OH COME ON. Again?! I JUST got settled in.`

---

**Story 2 — Mood selection**
> As a developer, I want to pick a specific mood that fits my app's personality, so that the exit message feels intentional.

```python
tantrumpy.enable(mood="philosophy")
# exit output: 🧠 To exit is to finally understand the void.
```

---

**Story 3 — Crash roasting**
> As a developer, I want my app to roast itself when it crashes on an unhandled exception, so that even failures feel entertaining.

```
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    result = 1 / 0
ZeroDivisionError: division by zero

💀 You really wrote THAT code and expected it to work?
```

---

**Story 4 — Verbose exit context**
> As a developer, I want to optionally see what triggered the exit (Ctrl+C vs sys.exit vs crash), so that I can debug while still being entertained.

```python
tantrumpy.enable(verbose=True)
# exit output: 😤 I JUST got settled in.  [exit via: SIGINT]
```

---

**Story 5 — Custom mood**
> As a developer, I want to add my own mood category with custom messages, so that the tantrum fits my project's specific voice.

```python
tantrumpy.add_messages(mood="corporate", messages=[
    "This action has been escalated to management.",
    "Please submit a ticket for this exit event.",
])
tantrumpy.enable(mood="corporate")
```

---

**Story 6 — CI/prod safe**
> As a DevOps engineer, I want to suppress tantrumpy output in CI pipelines without modifying code, so that logs stay clean.

```bash
TANTRUMPY_SILENT=1 python my_app.py
```

---

**Story 7 — Random mood per run**
> As a developer, I want a different random mood each time my app exits, so that it stays surprising and I don't get used to the same message.

```python
tantrumpy.enable()  # picks a different mood each invocation
```

---

**Story 8 — Clean disable**
> As a library author embedding tantrumpy, I want to programmatically disable it, so that I can control its lifecycle.

```python
tantrumpy.enable()
# ... do stuff
tantrumpy.disable()  # cleanly removes all signal hooks and atexit registration
```

---

## 6. Core Architecture & Patterns

### High-Level Architecture

```
User Code
    │
    └── tantrumpy.enable(mood, verbose)
              │
              ▼
        TantrumHandler (singleton)
              │
        ┌─────┴──────────────────────┐
        │  Hooks registered at enable() │
        │  - signal.SIGINT            │
        │  - signal.SIGTERM           │
        │  - atexit.register()        │
        │  - sys.excepthook           │
        └─────────────────────────────┘
              │
     (any exit event fires)
              │
              ▼
        _fired flag check ──── already fired? → skip
              │
              ▼
        picker.pick(mood, registry)
              │
              ▼
        colors.colorize(message, mood)
              │
              ▼
        print to sys.stderr
              │
              ▼
        resume normal exit / re-raise exception
```

### Directory Structure

```
tantrumpy/
├── tantrumpy/
│   ├── __init__.py      ← public API surface
│   ├── handler.py       ← TantrumHandler singleton + hook wiring
│   ├── messages.py      ← built-in mood message banks
│   ├── picker.py        ← message selection with no-repeat logic
│   └── colors.py        ← ANSI codes + supports_color() detection
├── examples/
│   └── demo.py          ← runnable demo for each mood and trigger
├── tests/
│   ├── test_handler.py
│   ├── test_messages.py
│   ├── test_picker.py
│   └── test_colors.py
├── pyproject.toml
└── README.md
```

### Key Design Patterns

- **Singleton handler**: `TantrumHandler` is module-level — only one instance exists; `enable()` reconfigures it, `disable()` tears it down.
- **`_fired` guard**: Boolean flag prevents double-firing when multiple hooks trigger simultaneously (e.g., SIGINT + atexit).
- **Non-blocking**: Every hook re-raises or continues the original exit flow after firing the tantrum. tantrumpy is a side-effect, never a gatekeeper.
- **Registry pattern**: Custom moods are stored in a shared `_registry` dict that merges with built-in mood banks.
- **No global state leakage**: `disable()` fully restores original signal handlers, atexit list, and `sys.excepthook`.

---

## 7. Features

### Feature 1: Signal Hooks

| Hook | Method | Catches |
|------|--------|---------|
| SIGINT | `signal.signal(SIGINT, _handler)` | Ctrl+C |
| SIGTERM | `signal.signal(SIGTERM, _handler)` | `kill <pid>` |
| Normal exit | `atexit.register(_handler)` | `sys.exit()`, end of script |
| Crash | Replace `sys.excepthook` | Unhandled exceptions |

### Feature 2: Message System

- 6 built-in moods × 15+ messages each = 90+ built-in messages at launch
- Messages are plain strings stored in `messages.py` as a `dict[str, list[str]]`
- Custom moods are added via `tantrumpy.add_messages()` and merged into the registry

### Feature 3: Picker (No-Repeat)

- Per-mood shuffled queue; when queue is exhausted, reshuffled
- `mood="random"` randomly selects a mood key first, then a message
- Session-scoped (resets on new Python process)

### Feature 4: Colored Output

**Default:** Colored. **Fallback:** Plain text.

Color map:

| Mood | Emoji | ANSI Color |
|------|-------|-----------|
| frustrated | 😤 | Red (`\033[31m`) |
| rude | 💀 | Magenta (`\033[35m`) |
| comic | 🎭 | Cyan (`\033[36m`) |
| cringe | 😬 | Yellow (`\033[33m`) |
| philosophy | 🧠 | Blue (`\033[34m`) |
| dramatic | 🎬 | Bright Red (`\033[91m`) |

Fallback triggers:
- `not sys.stderr.isatty()` — piped/redirected output
- `os.environ.get("NO_COLOR")` — NO_COLOR standard
- `os.environ.get("TERM") == "dumb"` — dumb terminal
- Windows without ANSI support detected

### Feature 5: Verbose Mode

When `verbose=True`, appends the exit trigger source:

```
😤 I JUST got settled in.  [exit via: SIGINT]
😤 I JUST got settled in.  [exit via: sys.exit(1)]
😤 I JUST got settled in.  [exit via: exception: ZeroDivisionError]
```

### Feature 6: Silent Mode

`TANTRUMPY_SILENT=1` environment variable — tantrumpy registers hooks but prints nothing. Safe for production and CI without code changes.

---

## 8. Technology Stack

### Core
- **Language:** Python >= 3.8
- **Build system:** `hatchling` (via `pyproject.toml`)
- **Runtime dependencies:** None

### Standard Library Used
| Module | Purpose |
|--------|---------|
| `signal` | SIGINT / SIGTERM hooks |
| `atexit` | sys.exit() / normal end hook |
| `sys` | excepthook, stderr output |
| `os` | env var checks for color fallback |
| `random` | message shuffling |

### Dev Dependencies
| Package | Purpose |
|---------|---------|
| `pytest` | Unit and integration tests |
| `pytest-cov` | Coverage reporting |

### No Optional Dependencies
tantrumpy deliberately avoids `colorama`, `rich`, `click`, or any other optional library. ANSI codes are written directly.

---

## 9. Security & Configuration

### Configuration (Environment Variables)

| Variable | Default | Effect |
|----------|---------|--------|
| `TANTRUMPY_SILENT` | unset | Set to `1` to suppress all output |
| `NO_COLOR` | unset | Set to any value to disable ANSI colors (industry standard) |
| `TERM` | varies | `dumb` disables colors |

### Security Scope

**In scope:**
- ✅ Safe handling of signal interruptions (no signal handler crashes)
- ✅ No file I/O, no network calls, no subprocess spawning
- ✅ Prints only to `stderr`, never `stdout`
- ✅ Does not swallow exceptions or hide error information

**Out of scope:**
- ❌ Authentication or authorization (not applicable)
- ❌ Input sanitization for custom messages (trust the developer)
- ❌ Sandboxing custom mood callbacks

### Deployment Considerations
- Safe to include in production code when `TANTRUMPY_SILENT=1` is set
- Does not affect process exit codes
- Compatible with Docker, systemd, and any process manager (exits cleanly)

---

## 10. API Specification

### Public API (`tantrumpy/__init__.py`)

#### `tantrumpy.enable(mood="random", verbose=False)`

Registers all exit hooks and activates tantrumpy.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mood` | `str` | `"random"` | Mood key. Built-in: `frustrated`, `rude`, `comic`, `cringe`, `philosophy`, `dramatic`. Also accepts any custom mood added via `add_messages()`. |
| `verbose` | `bool` | `False` | If `True`, appends exit trigger source to the message. |

```python
tantrumpy.enable()
tantrumpy.enable(mood="rude")
tantrumpy.enable(mood="random", verbose=True)
```

---

#### `tantrumpy.disable()`

Removes all hooks registered by `enable()`. Restores original signal handlers and `sys.excepthook`.

```python
tantrumpy.disable()
```

---

#### `tantrumpy.add_messages(mood, messages)`

Registers a new mood or appends messages to an existing mood.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mood` | `str` | Mood key (new or existing) |
| `messages` | `list[str]` | List of message strings |

```python
tantrumpy.add_messages(
    mood="corporate",
    messages=[
        "This exit event has been logged for review.",
        "Please submit a ticket for this disruption.",
    ]
)
tantrumpy.enable(mood="corporate")
```

---

### Internal Module Interfaces

#### `picker.pick(mood: str, registry: dict) -> str`
Returns a single message string. Handles shuffling and rotation.

#### `colors.colorize(message: str, mood: str) -> str`
Returns ANSI-colored string, or plain string if color not supported.

#### `colors.supports_color() -> bool`
Returns `True` if stderr supports ANSI color codes.

---

## 11. Success Criteria

### MVP Success Definition
A developer can `pip install tantrumpy`, add `tantrumpy.enable()` to any Python script, and see a colored, emotional exit message on every exit trigger — with zero additional configuration.

### Functional Requirements
- ✅ `pip install tantrumpy` works from PyPI
- ✅ `tantrumpy.enable()` activates in one line
- ✅ All 4 exit triggers fire the tantrum (SIGINT, SIGTERM, sys.exit, crash)
- ✅ All 6 built-in moods produce valid messages
- ✅ Custom moods work via `add_messages()`
- ✅ `disable()` fully restores original handlers
- ✅ `TANTRUMPY_SILENT=1` suppresses all output
- ✅ Color output works on supported terminals
- ✅ Plain text fallback works on dumb terminals and piped output
- ✅ Double-fire guard works (no duplicate messages)
- ✅ Exit codes are never modified

### Quality Indicators
- Test coverage >= 80%
- Zero runtime dependencies in final package
- Package size < 50KB
- Import time < 10ms

### User Experience Goals
- Reading the README takes < 2 minutes
- Time from `pip install` to first tantrum: < 1 minute
- Messages feel genuinely funny, not forced

---

## 12. Implementation Phases

### Phase 1 — Package Scaffold & Core Logic
**Goal:** Installable package with message system and picker working.

- ✅ `pyproject.toml` with correct metadata
- ✅ `tantrumpy/colors.py` — ANSI codes + `supports_color()`
- ✅ `tantrumpy/messages.py` — all 6 moods × 15+ messages
- ✅ `tantrumpy/picker.py` — shuffle/rotate picker + custom registry
- ✅ `pip install -e .` works locally

**Validation:** `python -c "from tantrumpy.picker import pick; print(pick('rude', {}))"` returns a message.

---

### Phase 2 — Hook System & Public API
**Goal:** All 4 exit triggers work, public API is complete.

- ✅ `tantrumpy/handler.py` — TantrumHandler with all 4 hooks
- ✅ `_fired` double-fire guard
- ✅ `tantrumpy/__init__.py` — `enable()`, `disable()`, `add_messages()`
- ✅ `verbose=True` exit context appended
- ✅ `TANTRUMPY_SILENT=1` suppression

**Validation:** Run `python -c "import tantrumpy; tantrumpy.enable(); import sys; sys.exit()"` and see tantrum output.

---

### Phase 3 — Tests & Examples
**Goal:** Test suite passes, demo script is polished.

- ✅ `tests/test_messages.py` — all moods have >= 15 messages
- ✅ `tests/test_picker.py` — no-repeat logic, random mood, custom moods
- ✅ `tests/test_handler.py` — enable/disable, double-fire guard, silent mode
- ✅ `tests/test_colors.py` — colorize output, fallback logic
- ✅ `examples/demo.py` — demonstrates each mood and each trigger type

**Validation:** `pytest tests/` — all tests pass.

---

### Phase 4 — Polish & Publish
**Goal:** Package is ready for PyPI and community use.

- ✅ `README.md` with quick start, full API reference, mood table
- ✅ `CLAUDE.md` updated with project context
- ✅ Package published to PyPI (`pip install tantrumpy`)
- ✅ GitHub repo with examples in README

**Validation:** `pip install tantrumpy` from PyPI, fresh environment, demo works.

---

## 13. Future Considerations

### v2 Features
- **Multi-line rant mode** — `style="rant"` for 2-4 line dramatic monologues
- **Logging integration** — `tantrumpy.LogHandler` as a `logging.Handler` subclass
- **Async support** — asyncio-compatible signal handling for async apps

### Integration Opportunities
- **Flask/FastAPI middleware** — tantrum on app shutdown
- **pytest plugin** — tantrum after test suite completes (pass or fail)
- **Click integration** — auto-tantrum on CLI app exit

### Advanced Features
- **Community mood packs** — installable message extensions (`pip install tantrumpy-extra-moods`)
- **Locale/language support** — messages in other languages
- **Webhook mode** — POST the message to Slack/Discord on exit (for team entertainment)
- **Exit code awareness** — different message tone based on exit code (0 = peaceful, non-zero = furious)

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Signal handler conflicts | Another library also replaces SIGINT — tantrumpy overwrites it silently | Chain original handlers: store the previous handler and call it after firing the tantrum |
| `atexit` + signal double-fire | Both atexit and SIGINT fire, printing two messages | `_fired` boolean flag — first hook to fire wins, rest are no-ops |
| Windows compatibility | ANSI color codes don't work on older Windows terminals | `supports_color()` detects Windows without ANSI support and falls back to plain text |
| Crash hook hides tracebacks | Replacing `sys.excepthook` might interfere with other tools (Sentry, Rollbar) | Chain original excepthook: call `sys.__excepthook__` after printing tantrum |
| PyPI name conflict | `tantrumpy` already taken on PyPI | Check before publishing; fallback names: `py-tantrumpy`, `tantrumlib` |

---

## 15. Appendix

### Related Documents
- Architecture Plan: `/home/dev-hemup/.claude/plans/compressed-yawning-lightning.md`

### Project Structure
```
/home/dev-hemup/project/tantrumpy/
├── tantrumpy/           ← package source
├── examples/            ← demo scripts
├── tests/               ← test suite
├── .claude/
│   └── PRD.md           ← this document
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

### Key Technical References
- [NO_COLOR standard](https://no-color.org/) — env var convention for disabling color
- [Python signal module](https://docs.python.org/3/library/signal.html)
- [Python atexit module](https://docs.python.org/3/library/atexit.html)
- [Python sys.excepthook](https://docs.python.org/3/library/sys.html#sys.excepthook)
- [pyproject.toml spec](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
