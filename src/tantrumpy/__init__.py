"""
tantrumpy — Your Python app's last words.

Drop one line into any Python app and give it a voice on exit.

    import tantrumpy
    tantrumpy.enable()

That's it.
"""

from typing import Dict, List

from tantrumpy import picker as _picker
from tantrumpy.handler import _handler
from tantrumpy.messages import MoodBank

__version__ = "1.0.0"
__all__ = ["enable", "disable", "add_messages"]

# Internal custom mood storage — MoodBank keeps emoji + messages together
_custom_banks: Dict[str, MoodBank] = {}


def enable(mood: str = "random", verbose: bool = False) -> None:
    """
    Activate tantrumpy — register all exit hooks.

    Args:
        mood:    Which mood to use on exit. One of: "frustrated", "rude",
                 "comic", "cringe", "philosophy", "dramatic", "random",
                 or any custom mood added via add_messages().
                 Defaults to "random".
        verbose: If True, appends the exit trigger type to the message
                 e.g. "  [exit via: SIGINT (Ctrl+C)]"
    """
    _handler.enable(
        mood=mood,
        verbose=verbose,
        custom=_custom_banks if _custom_banks else None,
    )


def disable() -> None:
    """
    Deactivate tantrumpy — restore original signal handlers.

    Safe to call even if enable() was never called.
    """
    _handler.disable()


def add_messages(mood: str, messages: List[str], emoji: str = "") -> None:
    """
    Add custom messages to a mood bank.

    Creates a new mood if it doesn't exist, or appends to an existing one.
    Call this before enable() for messages to take effect.

    Args:
        mood:     The mood key (e.g. "boss", "corporate", or an existing mood).
        messages: List of message strings to add.
        emoji:    Optional emoji prefix for this mood (e.g. "📋").
                  Defaults to "" (no emoji). Ignored when appending to a
                  mood that already has an emoji unless explicitly overriding.

    Example:
        tantrumpy.add_messages("corporate", [
            "This exit event has been logged for review.",
            "Please submit a ticket for this disruption.",
        ], emoji="📋")
        tantrumpy.enable(mood="corporate")
    """
    if not isinstance(mood, str) or not mood.strip():
        raise ValueError("mood must be a non-empty string.")
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list of strings.")
    if not all(isinstance(m, str) and m.strip() for m in messages):
        raise ValueError("All items in messages must be non-empty strings.")

    if mood in _custom_banks:
        _custom_banks[mood]["messages"].extend(messages)
        if emoji:
            _custom_banks[mood]["emoji"] = emoji
    else:
        _custom_banks[mood] = {"emoji": emoji, "messages": list(messages)}

    # Refresh registry so picker knows about the updated mood
    _picker.reset()
