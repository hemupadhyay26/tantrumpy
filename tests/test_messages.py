"""Tests for tantrumpy/messages.py — message bank integrity."""

from tantrumpy.messages import MOODS

REQUIRED_MOODS = {"frustrated", "rude", "comic", "cringe", "philosophy", "dramatic"}


def test_all_required_moods_present():
    assert REQUIRED_MOODS.issubset(set(MOODS.keys()))


def test_each_mood_has_minimum_15_messages():
    for mood, bank in MOODS.items():
        assert len(bank["messages"]) >= 15, (
            f"Mood '{mood}' only has {len(bank['messages'])} messages"
        )


def test_no_empty_messages():
    for mood, bank in MOODS.items():
        for msg in bank["messages"]:
            assert isinstance(msg, str) and msg.strip(), (
                f"Empty or non-string message found in mood '{mood}'"
            )


def test_no_duplicate_messages_within_mood():
    for mood, bank in MOODS.items():
        msgs = bank["messages"]
        assert len(msgs) == len(set(msgs)), f"Duplicate messages found in mood '{mood}'"


def test_all_moods_have_emoji():
    for mood, bank in MOODS.items():
        assert bank["emoji"].strip(), f"Empty emoji for mood '{mood}'"


def test_mood_bank_has_required_keys():
    for mood, bank in MOODS.items():
        assert "emoji" in bank, f"Mood '{mood}' missing 'emoji' key"
        assert "messages" in bank, f"Mood '{mood}' missing 'messages' key"
