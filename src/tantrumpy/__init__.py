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

__version__ = "1.0.0"
__all__ = ["enable", "disable", "add_messages"]

# Internal custom mood storage
_custom_messages: Dict[str, List[str]] = {}


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
        custom=_custom_messages if _custom_messages else None,
    )


def disable() -> None:
    """
    Deactivate tantrumpy — restore original signal handlers.

    Safe to call even if enable() was never called.
    """
    _handler.disable()


def add_messages(mood: str, messages: List[str]) -> None:
    """
    Add custom messages to a mood bank.

    Creates a new mood if it doesn't exist, or appends to an existing one.
    Call this before enable() for messages to take effect.

    Args:
        mood:     The mood key (e.g. "boss", "corporate", or an existing mood).
        messages: List of message strings to add.

    Example:
        tantrumpy.add_messages("corporate", [
            "This exit event has been logged for review.",
            "Please submit a ticket for this disruption.",
        ])
        tantrumpy.enable(mood="corporate")
    """
    if not isinstance(mood, str) or not mood.strip():
        raise ValueError("mood must be a non-empty string.")
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list of strings.")
    if not all(isinstance(m, str) and m.strip() for m in messages):
        raise ValueError("All items in messages must be non-empty strings.")
    if mood in _custom_messages:
        _custom_messages[mood].extend(messages)
    else:
        _custom_messages[mood] = list(messages)
    # Refresh registry so picker knows about the new mood
    _picker.reset()
