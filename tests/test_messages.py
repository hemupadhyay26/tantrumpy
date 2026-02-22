"""Tests for tantrumpy/messages.py — message bank integrity."""
from tantrumpy.messages import MESSAGES, MOOD_EMOJIS

REQUIRED_MOODS = {"frustrated", "rude", "comic", "cringe", "philosophy", "dramatic"}


def test_all_required_moods_present():
    assert REQUIRED_MOODS.issubset(set(MESSAGES.keys()))


def test_each_mood_has_minimum_15_messages():
    for mood, msgs in MESSAGES.items():
        assert len(msgs) >= 15, f"Mood '{mood}' only has {len(msgs)} messages"


def test_no_empty_messages():
    for mood, msgs in MESSAGES.items():
        for msg in msgs:
            assert isinstance(msg, str) and msg.strip(), (
                f"Empty or non-string message found in mood '{mood}'"
            )


def test_no_duplicate_messages_within_mood():
    for mood, msgs in MESSAGES.items():
        assert len(msgs) == len(set(msgs)), (
            f"Duplicate messages found in mood '{mood}'"
        )


def test_all_moods_have_emoji():
    for mood in MESSAGES:
        assert mood in MOOD_EMOJIS, f"No emoji defined for mood '{mood}'"
        assert MOOD_EMOJIS[mood].strip(), f"Empty emoji for mood '{mood}'"
