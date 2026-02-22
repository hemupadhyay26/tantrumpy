# tantrumpy — Development Best Practices

Reference guide for contributors and maintainers of the tantrumpy codebase.

---

## 1. Project Principles (Non-Negotiable)

| Principle | Rule |
|-----------|------|
| Zero runtime deps | Never add an `import` that isn't in Python stdlib |
| Never block exit | tantrumpy is a side-effect, not a gatekeeper — always let the process die normally |
| Stderr only | All output goes to `sys.stderr`. Never print to `sys.stdout` |
| One-line API | `tantrumpy.enable()` must always work with zero arguments |
| Fail silently | If tantrumpy itself crashes internally, swallow the error — never surface it to the user's app |

---

## 2. Module Responsibilities

Each module has a single, clear responsibility. Do not mix concerns.

| Module | Owns | Must NOT |
|--------|------|----------|
| `colors.py` | ANSI codes, color detection | Know about moods, messages, or hooks |
| `messages.py` | Raw message data | Contain any logic — data only |
| `picker.py` | Selection logic, registry | Know about signals or output |
| `handler.py` | Signal/atexit wiring | Know about message content |
| `__init__.py` | Public API surface | Contain business logic |

---

## 3. Type Annotations

**All functions and module-level variables must be fully typed.**

### Use specific types, not bare generics

```python
# BAD
MESSAGES: dict = {...}
def pick(mood, custom=None): ...

# GOOD
MESSAGES: Dict[str, List[str]] = {...}
def pick(mood: str, custom: Optional[Dict[str, List[str]]] = None) -> str: ...
```

### Use `Optional` for nullable parameters

```python
# BAD
def enable(custom=None): ...

# GOOD
def enable(custom: Optional[Dict[str, List[str]]] = None) -> None: ...
```

### Prefer precise signal types over `Any`

```python
# BAD
def _on_sigint(self, signum: int, frame: Any) -> None: ...

# GOOD
def _on_sigint(self, signum: int, frame: Optional[types.FrameType]) -> None: ...
```

### Python 3.8 compatibility

Use `from typing import ...` — do NOT use the `X | Y` union syntax or `list[str]` lowercase generics (requires Python 3.10+).

```python
# BAD (3.10+ only)
def pick(mood: str, custom: dict[str, list[str]] | None = None) -> str: ...

# GOOD (3.8+)
from typing import Dict, List, Optional
def pick(mood: str, custom: Optional[Dict[str, List[str]]] = None) -> str: ...
```

---

## 4. Runtime Validation

Validate at the **public API boundary only** (`__init__.py`). Internal modules trust their inputs.

### Pattern: validate then assign

```python
def add_messages(mood: str, messages: List[str]) -> None:
    if not isinstance(mood, str) or not mood.strip():
        raise ValueError("mood must be a non-empty string.")
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list of strings.")
    if not all(isinstance(m, str) and m.strip() for m in messages):
        raise ValueError("All items in messages must be non-empty strings.")
    # safe to proceed...
```

### What to validate at the API boundary

- `mood` — must be `str`, non-empty
- `messages` — must be `list[str]`, non-empty, no blank items
- Do NOT validate internal function arguments (picker, handler internals)

---

## 5. Error Handling

### Public API — raise `ValueError` with clear messages

```python
raise ValueError("mood must be a non-empty string.")
raise ValueError(f"Unknown mood: '{mood}'. Available: {list(_registry.keys())}")
```

### Internal hooks — swallow all exceptions silently

The `_fire()` method wraps its body in a bare `except Exception: return`.
This is intentional — tantrumpy must never crash the host application.

```python
def _fire(self, trigger: str) -> None:
    ...
    try:
        message = _picker.pick(resolved_mood, self._custom)
        emoji   = _picker.get_emoji(resolved_mood)
    except Exception:
        return  # never crash the app just to print a tantrum
```

**Do not** add logging, re-raise, or print inside this except block.

---

## 6. The `_fired` Guard

`TantrumHandler._fired` is a boolean that prevents the tantrum from printing twice when multiple hooks trigger simultaneously (e.g., SIGINT + atexit both fire on Ctrl+C).

### Rules:
- Set `_fired = True` as the **first** thing inside `_fire()` after the early-return check
- Reset `_fired = False` in `enable()` and `disable()`
- Always reset in tests via the `reset_state` fixture

```python
def _fire(self, trigger: str) -> None:
    if self._fired:       # guard first
        return
    self._fired = True    # set immediately
    ...
```

---

## 7. Signal Handler Rules

### Always chain the original handler

When handling SIGINT/SIGTERM, restore the original handler and re-raise the signal so the process exits naturally:

```python
def _on_sigint(self, signum: int, frame: Optional[types.FrameType]) -> None:
    self._fire("SIGINT (Ctrl+C)")
    signal.signal(signal.SIGINT, self._orig_sigint)  # restore
    signal.raise_signal(signal.SIGINT)               # re-raise
```

### Always chain the original excepthook

```python
def _on_exception(self, exc_type, exc_value, exc_tb) -> None:
    self._orig_excepthook(exc_type, exc_value, exc_tb)  # traceback first
    self._fire(f"exception: {exc_type.__name__}")        # tantrum after
```

**Never suppress the original behavior.**

---

## 8. Adding a New Mood

To add a new built-in mood, touch exactly **3 places**:

1. **`messages.py`** — add the mood key with 15+ messages
   ```python
   "sarcastic": [
       "Oh wow, another exit. How totally unexpected.",
       ...  # 14 more
   ]
   ```

2. **`messages.py`** — add the emoji in `MOOD_EMOJIS`
   ```python
   "sarcastic": "🙄",
   ```

3. **`colors.py`** — add the ANSI color in `MOOD_COLORS`
   ```python
   "sarcastic": "\033[32m",  # Green
   ```

That's it. The picker, handler, and API all work dynamically from the registry.

---

## 9. Environment Variables

| Variable | Effect | Where checked |
|----------|--------|---------------|
| `TANTRUMPY_SILENT` | Suppress all output | `handler.py::_fire()` |
| `NO_COLOR` | Disable ANSI colors | `colors.py::supports_color()` |
| `TERM=dumb` | Disable ANSI colors | `colors.py::supports_color()` |
| `WT_SESSION` / `ANSICON` | Windows ANSI detection | `colors.py::supports_color()` |

Never read env vars outside of these designated places.

---

## 10. Code Style

- **Python 3.8+** — no walrus operator (`:=`), no `match` statements, no `X | Y` union syntax
- **No f-strings with complex expressions** — keep f-strings readable
- **No global state outside designated module-level vars** — `_queues`, `_registry`, `_handler` are the only permitted globals
- **Private by convention** — prefix internal functions/vars with `_`. Public API is only what's in `__init__.py::__all__`
- **Docstrings on all public functions** — one-line summary + Args/Returns if non-obvious
