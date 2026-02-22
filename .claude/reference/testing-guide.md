# tantrumpy — Testing Guide

Complete reference for writing, organizing, and running tests for tantrumpy.

---

## 1. Test Stack

| Tool | Role |
|------|------|
| `pytest` | Test runner and assertions |
| `pytest-cov` | Coverage reporting |
| `unittest.mock` | Mocking stdlib (signal, sys, os) — no extra deps needed |
| `monkeypatch` | pytest fixture for env vars and attribute patching |

Run tests:
```bash
uv run pytest tests/ -v                          # all tests, verbose
uv run pytest tests/ --cov=src/tantrumpy         # with coverage
uv run pytest tests/test_picker.py -v            # single file
uv run pytest tests/ -k "test_pick"              # filter by name
```

---

## 2. Test File Organization

One test file per source module. 1:1 mapping.

```
tests/
├── conftest.py          # shared fixtures (reset_state)
├── test_colors.py       # covers src/tantrumpy/colors.py
├── test_messages.py     # covers src/tantrumpy/messages.py
├── test_picker.py       # covers src/tantrumpy/picker.py
└── test_handler.py      # covers src/tantrumpy/handler.py
```

---

## 3. Naming Convention

```
test_<what>_<condition>
```

| Pattern | Example |
|---------|---------|
| Happy path | `test_pick_returns_string` |
| Specific input | `test_pick_valid_message_from_mood` |
| Edge case | `test_pick_unknown_mood_raises` |
| Negative / guard | `test_fire_only_once` |
| Env var behavior | `test_silent_mode_suppresses_output` |
| State reset | `test_reset_clears_state` |

---

## 4. The `reset_state` Fixture (Always Active)

Defined in `conftest.py`. Runs automatically before and after **every** test via `autouse=True`.

```python
@pytest.fixture(autouse=True)
def reset_state():
    picker.reset()
    _handler.disable()
    _handler._fired = False
    yield
    _handler.disable()
    _handler._fired = False
    picker.reset()
```

**Why it matters:**
tantrumpy uses module-level singletons (`_handler`, `_registry`, `_queues`).
Without resetting between tests, state bleeds across test cases causing false passes or false failures.

---

## 5. Critical Testing Rules

### NEVER call `sys.exit()` in tests
It will actually exit the test process. Mock it instead.

```python
# BAD
sys.exit(0)  # kills pytest

# GOOD
with patch("sys.exit") as mock_exit:
    tantrumpy.enable()
    mock_exit.assert_called()
```

### NEVER send real OS signals in tests
Sending `SIGINT` to the test process will interrupt pytest. Patch the handler.

```python
# BAD
os.kill(os.getpid(), signal.SIGINT)  # kills pytest

# GOOD
with patch.object(_handler, "_fire") as mock_fire:
    _handler._on_sigint(signal.SIGINT, None)
    mock_fire.assert_called_once_with("SIGINT (Ctrl+C)")
```

### NEVER test print output by capturing stdout
tantrumpy prints to `stderr`. Use `capsys` or patch `builtins.print`.

```python
# GOOD — capture stderr
def test_output_goes_to_stderr(capsys, monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="comic")
    _handler._fired = False
    _handler._fire("test")
    captured = capsys.readouterr()
    assert captured.out == ""     # nothing on stdout
    assert captured.err != ""     # something on stderr
```

---

## 6. Mocking Patterns

### Mock environment variables with `monkeypatch`

```python
def test_silent_mode(monkeypatch):
    monkeypatch.setenv("TANTRUMPY_SILENT", "1")
    # ... test body
    # monkeypatch auto-restores after test
```

```python
def test_no_color_env(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.delenv("TERM", raising=False)  # remove if set
```

### Mock `isatty()` for color tests

```python
from unittest.mock import patch

def test_color_when_tty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    with patch.object(sys.stderr, "isatty", return_value=True):
        assert supports_color() is True

def test_no_color_when_piped():
    with patch.object(sys.stderr, "isatty", return_value=False):
        assert supports_color() is False
```

### Mock `print` to capture tantrum output

```python
def test_verbose_output(monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="dramatic", verbose=True)
    _handler._fired = False

    printed = []
    with patch("builtins.print", side_effect=lambda *a, **kw: printed.append(a)):
        _handler._fire("SIGINT (Ctrl+C)")

    assert printed, "Expected at least one print call"
    assert "[exit via: SIGINT (Ctrl+C)]" in printed[0][0]
```

### Mock `sys.excepthook` to test exception chaining

```python
from unittest.mock import MagicMock

def test_original_excepthook_called():
    original = MagicMock()
    _handler.enable(mood="rude")
    _handler._orig_excepthook = original
    _handler._fired = False

    with patch.object(_handler, "_fire"):
        _handler._on_exception(ValueError, ValueError("test"), None)

    original.assert_called_once_with(ValueError, ValueError("test"), None)
```

---

## 7. Coverage Strategy

### Target: >= 80% overall, 100% on `messages.py` and `colors.py`

Run coverage:
```bash
uv run pytest tests/ --cov=src/tantrumpy --cov-report=term-missing
```

Expected output shape:
```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/tantrumpy/__init__.py            20      1    95%
src/tantrumpy/colors.py              18      0   100%
src/tantrumpy/handler.py             45      4    91%
src/tantrumpy/messages.py             4      0   100%
src/tantrumpy/picker.py              30      2    93%
-----------------------------------------------------
TOTAL                               117      7    94%
```

### What must be 100% covered

- `messages.py` — pure data, trivial to cover
- `colors.py` — all branches of `supports_color()` and `colorize()`

### Acceptable gaps (hard to test without subprocess)

- `_on_sigint` / `_on_sigterm` — the `signal.raise_signal()` line (re-raises OS signal)
- Windows ANSI branch in `supports_color()` unless running on Windows CI

### Generate HTML report

```bash
uv run pytest tests/ --cov=src/tantrumpy --cov-report=html
# opens htmlcov/index.html
```

---

## 8. Test Case Examples by Module

### `test_messages.py` — data integrity tests

```python
from tantrumpy.messages import MESSAGES, MOOD_EMOJIS

def test_each_mood_has_minimum_15_messages():
    for mood, msgs in MESSAGES.items():
        assert len(msgs) >= 15, f"Mood '{mood}' only has {len(msgs)} messages"

def test_no_empty_messages():
    for mood, msgs in MESSAGES.items():
        for msg in msgs:
            assert isinstance(msg, str) and msg.strip()

def test_no_duplicate_messages_within_mood():
    for mood, msgs in MESSAGES.items():
        assert len(msgs) == len(set(msgs)), f"Duplicates in '{mood}'"

def test_all_moods_have_emoji():
    for mood in MESSAGES:
        assert mood in MOOD_EMOJIS
```

---

### `test_colors.py` — branch coverage for color detection

```python
def test_no_color_when_not_tty():
    with patch.object(sys.stderr, "isatty", return_value=False):
        assert supports_color() is False

def test_no_color_when_env_set(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    with patch.object(sys.stderr, "isatty", return_value=True):
        assert supports_color() is False

def test_no_color_when_dumb_term(monkeypatch):
    monkeypatch.setenv("TERM", "dumb")
    with patch.object(sys.stderr, "isatty", return_value=True):
        assert supports_color() is False

def test_colorize_returns_plain_when_unsupported(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    with patch.object(sys.stderr, "isatty", return_value=True):
        assert colorize("hello", "frustrated") == "hello"

def test_colorize_wraps_ansi_when_supported(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("TERM", raising=False)
    with patch.object(sys.stderr, "isatty", return_value=True):
        with patch("os.name", "posix"):
            result = colorize("hello", "frustrated")
            assert "\033[31m" in result   # Red
            assert "\033[0m" in result    # Reset
```

---

### `test_picker.py` — selection logic and no-repeat

```python
def test_pick_returns_valid_message():
    result = pick("comic")
    assert result in MESSAGES["comic"]

def test_pick_random_selects_from_any_mood():
    result = pick("random")
    all_msgs = [m for msgs in MESSAGES.values() for m in msgs]
    assert result in all_msgs

def test_no_consecutive_repeats():
    seen = [pick("frustrated") for _ in range(10)]
    dupes = sum(1 for i in range(len(seen) - 1) if seen[i] == seen[i + 1])
    assert dupes == 0

def test_full_rotation_before_repeat():
    mood = "comic"
    n = len(MESSAGES[mood])
    seen = [pick(mood) for _ in range(n)]
    assert len(set(seen)) == n   # all unique in first full pass

def test_unknown_mood_raises():
    with pytest.raises(ValueError, match="Unknown mood"):
        pick("not_a_real_mood")

def test_custom_mood_works():
    custom = {"test": ["Hello from custom."]}
    result = pick("test", custom=custom)
    assert result == "Hello from custom."
```

---

### `test_handler.py` — hook wiring and fire guard

```python
def test_enable_sets_active():
    _handler.enable()
    assert _handler._active is True

def test_disable_restores_state():
    _handler.enable()
    _handler.disable()
    assert _handler._active is False

def test_fire_only_once(monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="comic")
    _handler._fired = False

    with patch("builtins.print") as mock_print:
        _handler._fire("first")
        _handler._fire("second")   # should be no-op
        assert mock_print.call_count == 1

def test_silent_suppresses_output(monkeypatch):
    monkeypatch.setenv("TANTRUMPY_SILENT", "1")
    _handler.enable(mood="rude")
    _handler._fired = False

    with patch("builtins.print") as mock_print:
        _handler._fire("test")
        mock_print.assert_not_called()

def test_atexit_fires_tantrum():
    with patch.object(_handler, "_fire") as mock_fire:
        _handler._on_atexit()
        mock_fire.assert_called_once_with("sys.exit / normal exit")

def test_exception_hook_chains_original():
    original = MagicMock()
    _handler._orig_excepthook = original
    _handler._fired = False

    with patch.object(_handler, "_fire"):
        _handler._on_exception(RuntimeError, RuntimeError("boom"), None)

    original.assert_called_once()
```

---

## 9. Adding Tests for a New Mood

When adding a new mood to `messages.py`, the existing tests in `test_messages.py` automatically cover:
- Minimum message count (>= 15)
- No empty messages
- No duplicates
- Emoji present

You only need to add explicit tests if the new mood has special logic (it shouldn't).

---

## 10. CI Checklist

Before merging any change:

```bash
uv run pytest tests/ -v                                   # all 33 tests pass
uv run pytest tests/ --cov=src/tantrumpy --cov-fail-under=80  # coverage >= 80%
uv run python examples/demo.py --preview                  # visual sanity check
TANTRUMPY_SILENT=1 uv run python examples/demo.py         # silent mode works
```
