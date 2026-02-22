"""Tests for tantrumpy/__init__.py — public API surface."""

from unittest.mock import patch

import pytest

import tantrumpy
from tantrumpy import _custom_banks
from tantrumpy.handler import _handler


def test_enable_activates_handler():
    tantrumpy.enable()
    assert _handler._active is True


def test_enable_with_mood():
    tantrumpy.enable(mood="rude")
    assert _handler._mood == "rude"


def test_enable_with_verbose():
    tantrumpy.enable(verbose=True)
    assert _handler._verbose is True


def test_disable_deactivates_handler():
    tantrumpy.enable()
    tantrumpy.disable()
    assert _handler._active is False


def test_disable_safe_without_enable():
    tantrumpy.disable()  # should not raise


def test_add_messages_registers_custom_mood():
    tantrumpy.add_messages("test_custom", ["Hello from custom mood."])
    assert "test_custom" in _custom_banks
    assert "Hello from custom mood." in _custom_banks["test_custom"]["messages"]


def test_add_messages_appends_to_existing_mood():
    tantrumpy.add_messages("test_append", ["First message."])
    tantrumpy.add_messages("test_append", ["Second message."])
    assert len(_custom_banks["test_append"]["messages"]) == 2


def test_add_messages_with_emoji():
    tantrumpy.add_messages("corp", ["This exit was logged."], emoji="📋")
    assert _custom_banks["corp"]["emoji"] == "📋"
    assert "This exit was logged." in _custom_banks["corp"]["messages"]


def test_add_messages_emoji_updated_on_append():
    tantrumpy.add_messages("rebrand", ["First line."], emoji="🔵")
    tantrumpy.add_messages("rebrand", ["Second line."], emoji="🟢")
    assert _custom_banks["rebrand"]["emoji"] == "🟢"
    assert len(_custom_banks["rebrand"]["messages"]) == 2


def test_add_messages_emoji_not_overwritten_when_empty():
    tantrumpy.add_messages("stable", ["First line."], emoji="⭐")
    tantrumpy.add_messages("stable", ["Second line."])  # no emoji — keep existing
    assert _custom_banks["stable"]["emoji"] == "⭐"


def test_add_messages_invalid_mood_raises():
    with pytest.raises(ValueError, match="mood must be a non-empty string"):
        tantrumpy.add_messages("", ["Some message."])


def test_add_messages_empty_list_raises():
    with pytest.raises(ValueError, match="non-empty list"):
        tantrumpy.add_messages("valid_mood", [])


def test_add_messages_non_list_raises():
    with pytest.raises(ValueError, match="non-empty list"):
        tantrumpy.add_messages("valid_mood", "not a list")  # type: ignore


def test_add_messages_blank_string_item_raises():
    with pytest.raises(ValueError, match="non-empty strings"):
        tantrumpy.add_messages("valid_mood", ["   "])


def test_enable_passes_custom_messages_to_handler(monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    tantrumpy.add_messages("my_mood", ["Custom exit line."])
    tantrumpy.enable(mood="my_mood")
    assert _handler._custom is not None
    assert "my_mood" in _handler._custom
