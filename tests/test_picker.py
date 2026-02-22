"""Tests for tantrumpy/picker.py — selection logic."""
import pytest

from tantrumpy import picker
from tantrumpy.messages import MESSAGES


def test_pick_returns_string():
    result = picker.pick("frustrated")
    assert isinstance(result, str) and result.strip()


def test_pick_valid_message_from_mood():
    result = picker.pick("rude")
    assert result in MESSAGES["rude"]


def test_pick_all_moods():
    for mood in MESSAGES:
        result = picker.pick(mood)
        assert result in MESSAGES[mood]


def test_pick_random_mood():
    # mood="random" should return a valid message from any mood
    result = picker.pick("random")
    all_messages = [m for msgs in MESSAGES.values() for m in msgs]
    assert result in all_messages


def test_pick_unknown_mood_raises():
    with pytest.raises(ValueError, match="Unknown mood"):
        picker.pick("nonexistent_mood_xyz")


def test_no_consecutive_repeats():
    mood = "frustrated"
    seen = [picker.pick(mood) for _ in range(10)]
    consecutive_dupes = sum(1 for i in range(len(seen) - 1) if seen[i] == seen[i + 1])
    assert consecutive_dupes == 0


def test_all_messages_seen_before_repeat():
    mood = "comic"
    total = len(MESSAGES[mood])
    seen = [picker.pick(mood) for _ in range(total)]
    assert len(set(seen)) == total


def test_pick_custom_mood():
    custom = {"boss": ["Ship it.", "Deploy now."]}
    result = picker.pick("boss", custom=custom)
    assert result in custom["boss"]


def test_get_emoji_known_mood():
    picker.pick("frustrated")  # ensure registry is built
    assert picker.get_emoji("frustrated") == "😤"
    assert picker.get_emoji("rude") == "💀"


def test_get_emoji_unknown_mood_returns_empty():
    picker.pick("comic")  # ensure registry is built
    assert picker.get_emoji("does_not_exist") == ""


def test_all_moods_returns_list():
    moods = picker.all_moods()
    assert isinstance(moods, list)
    assert "frustrated" in moods


def test_reset_clears_state():
    picker.pick("dramatic")
    picker.reset()
    assert picker._registry == {}
    assert picker._queues == {}


def test_custom_extends_existing_builtin_mood():
    # Covers picker.py line 26: _registry[mood].extend(msgs) when mood already exists
    custom = {"frustrated": ["Extra frustrated message."]}
    result = picker.pick("frustrated", custom=custom)
    all_frustrated = MESSAGES["frustrated"] + custom["frustrated"]
    assert result in all_frustrated


def test_pick_with_custom_when_registry_already_built():
    # Covers picker.py line 53: elif custom — registry exists but custom is provided
    picker.pick("comic")  # builds registry without custom
    custom = {"brand_new": ["New custom message."]}
    result = picker.pick("brand_new", custom=custom)
    assert result == "New custom message."
