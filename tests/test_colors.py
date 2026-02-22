"""Tests for tantrumpy/colors.py — ANSI color support and fallback."""

import sys
from unittest.mock import patch

from tantrumpy.colors import MOOD_COLORS, RESET, colorize, supports_color


def test_supports_color_false_when_not_tty():
    with patch.object(sys.stderr, "isatty", return_value=False):
        assert supports_color() is False


def test_supports_color_false_when_no_color_set(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    with patch.object(sys.stderr, "isatty", return_value=True):
        assert supports_color() is False


def test_supports_color_false_when_dumb_term(monkeypatch):
    monkeypatch.setenv("TERM", "dumb")
    with patch.object(sys.stderr, "isatty", return_value=True):
        assert supports_color() is False


def test_colorize_returns_plain_when_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    with patch.object(sys.stderr, "isatty", return_value=True):
        result = colorize("hello", "frustrated")
        assert result == "hello"


def test_colorize_wraps_with_ansi_when_color_supported(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("TERM", raising=False)
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    with patch.object(sys.stderr, "isatty", return_value=True):
        with patch("os.name", "posix"):
            result = colorize("hello", "frustrated")
            assert MOOD_COLORS["frustrated"] in result
            assert RESET in result
            assert "hello" in result


def test_colorize_unknown_mood_returns_plain(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    with patch.object(sys.stderr, "isatty", return_value=True):
        result = colorize("hello", "nonexistent")
        assert result == "hello"


def test_supports_color_windows_with_wt_session(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("TERM", raising=False)
    monkeypatch.setenv("WT_SESSION", "some-session-id")
    with patch.object(sys.stderr, "isatty", return_value=True):
        with patch("os.name", "nt"):
            assert supports_color() is True


def test_supports_color_windows_without_ansi_support(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("TERM", raising=False)
    monkeypatch.delenv("WT_SESSION", raising=False)
    monkeypatch.delenv("ANSICON", raising=False)
    monkeypatch.delenv("ConEmuANSI", raising=False)
    with patch.object(sys.stderr, "isatty", return_value=True):
        with patch("os.name", "nt"):
            assert supports_color() is False
