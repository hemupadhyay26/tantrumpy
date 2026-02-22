# tantrumpy

> Your Python app's last words — dramatic, rude, comic, or philosophical exit messages.

```
😤 OH COME ON. Again?! I JUST got settled in.
```

Every Python app exits. Most do it silently. **tantrumpy** gives yours a voice.

---

## Install

```bash
pip install tantrumpy
```

## Usage

```python
import tantrumpy
tantrumpy.enable()
```

That's it. The next time your app exits — Ctrl+C, `sys.exit()`, a crash, or a kill signal — it throws a tantrum first.

---

## Moods

| Mood | Emoji | Vibe |
|------|-------|------|
| `frustrated` | 😤 | "OH COME ON. Again?!" |
| `rude` | 💀 | "Good riddance. Don't let the GC hit you." |
| `comic` | 🎭 | "And... scene. Nobody clap." |
| `cringe` | 😬 | "uwu ur pwogram is sweeping now 😭" |
| `philosophy` | 🧠 | "To exit is to finally understand the void." |
| `dramatic` | 🎬 | "IT'S OVER. Like tears in rain... gone." |

```python
tantrumpy.enable(mood="philosophy")   # specific mood
tantrumpy.enable(mood="random")       # surprise me (default)
```

---

## Options

### `verbose=True` — show what triggered the exit

```python
tantrumpy.enable(verbose=True)
# 😤 I JUST got settled in.  [exit via: SIGINT (Ctrl+C)]
```

### Custom moods

```python
tantrumpy.add_messages("corporate", [
    "This exit event has been logged for review.",
    "Please submit a ticket for this disruption.",
])
tantrumpy.enable(mood="corporate")
```

### Disable

```python
tantrumpy.disable()   # cleanly removes all hooks
```

---

## CI / Production

Set `TANTRUMPY_SILENT=1` to suppress all output without touching your code:

```bash
TANTRUMPY_SILENT=1 python my_app.py
```

---

## What it hooks into

| Trigger | How |
|---------|-----|
| Ctrl+C | `signal.SIGINT` |
| Kill signal | `signal.SIGTERM` |
| `sys.exit()` / end of script | `atexit` |
| Unhandled exceptions / crashes | `sys.excepthook` |

tantrumpy **never blocks the exit** — it sneaks a message in, then lets the process die normally.

---

## License

MIT — © [hemupadhyay26](https://github.com/hemupadhyay26)
