"""
Message selection logic for tantrumpy.
Picks a random message from a mood's bank with no immediate repeats.
"""
import random
from typing import Dict, List, Optional

from tantrumpy.messages import MESSAGES, MOOD_EMOJIS

# Per-session shuffle queues: mood -> shuffled list of indices
_queues: Dict[str, List[int]] = {}

# Merged registry: built-in + custom moods
_registry: Dict[str, List[str]] = {}
_emoji_registry: Dict[str, str] = {}


def _build_registry(custom: Optional[Dict[str, List[str]]] = None) -> None:
    """Merge built-in messages with any custom mood messages."""
    global _registry, _emoji_registry
    _registry = {mood: list(msgs) for mood, msgs in MESSAGES.items()}
    _emoji_registry = dict(MOOD_EMOJIS)
    if custom:
        for mood, msgs in custom.items():
            if mood in _registry:
                _registry[mood].extend(msgs)
            else:
                _registry[mood] = list(msgs)


def _get_queue(mood: str) -> List[int]:
    """Return (or create) a shuffled index queue for the mood."""
    if mood not in _queues or not _queues[mood]:
        indices = list(range(len(_registry[mood])))
        random.shuffle(indices)
        _queues[mood] = indices
    return _queues[mood]


def pick(mood: str, custom: Optional[Dict[str, List[str]]] = None) -> str:
    """
    Pick a random message for the given mood.

    - mood="random" selects a random mood first.
    - Rotates through all messages before repeating.
    - Supports custom mood banks via the `custom` dict.

    Returns the message string (without emoji prefix).
    """
    if not _registry:
        _build_registry(custom)
    elif custom:
        _build_registry(custom)

    if mood == "random":
        mood = random.choice(list(_registry.keys()))

    if mood not in _registry:
        raise ValueError(
            f"Unknown mood: '{mood}'. Available: {list(_registry.keys())}"
        )

    queue = _get_queue(mood)
    idx = queue.pop(0)
    return _registry[mood][idx]


def get_emoji(mood: str) -> str:
    """Return the emoji for a mood, or empty string for unknown moods."""
    return _emoji_registry.get(mood, "")


def all_moods() -> List[str]:
    """Return list of all available mood keys (built-in + custom)."""
    if not _registry:
        _build_registry()
    return list(_registry.keys())


def reset() -> None:
    """Reset all queues (used in tests)."""
    global _queues, _registry, _emoji_registry
    _queues = {}
    _registry = {}
    _emoji_registry = {}
