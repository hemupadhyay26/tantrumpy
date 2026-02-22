"""Tests for tantrumpy/handler.py — hook wiring and fire logic."""
import os
import signal
import sys
from unittest.mock import patch, MagicMock

import pytest

from tantrumpy.handler import _handler


def test_enable_sets_active():
    _handler.enable()
    assert _handler._active is True


def test_disable_clears_active():
    _handler.enable()
    _handler.disable()
    assert _handler._active is False


def test_disable_safe_when_not_enabled():
    _handler.disable()  # should not raise


def test_fire_only_once():
    _handler.enable(mood="comic")
    output = []

    with patch("sys.stderr") as mock_stderr:
        mock_stderr.isatty.return_value = False
        mock_stderr.write = lambda s: output.append(s)

        with patch("builtins.print") as mock_print:
            _handler._fire("test")
            _handler._fire("test again")  # should be no-op
            assert mock_print.call_count == 1


def test_silent_mode_suppresses_output(monkeypatch):
    monkeypatch.setenv("TANTRUMPY_SILENT", "1")
    _handler.enable(mood="rude")
    _handler._fired = False

    with patch("builtins.print") as mock_print:
        _handler._fire("test")
        mock_print.assert_not_called()


def test_verbose_mode_appends_trigger(monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="dramatic", verbose=True)
    _handler._fired = False

    printed = []
    with patch("builtins.print", side_effect=lambda *a, **kw: printed.append(a)):
        _handler._fire("SIGINT (Ctrl+C)")

    assert printed, "Expected print to be called"
    output = printed[0][0]
    assert "[exit via: SIGINT (Ctrl+C)]" in output


def test_on_atexit_fires(monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="philosophy")
    _handler._fired = False

    with patch.object(_handler, "_fire") as mock_fire:
        _handler._on_atexit()
        mock_fire.assert_called_once_with("sys.exit / normal exit")


def test_on_exception_calls_original_hook():
    original_hook = MagicMock()
    _handler.enable(mood="rude")
    _handler._orig_excepthook = original_hook
    _handler._fired = False

    exc_type = ValueError
    exc_value = ValueError("boom")
    exc_tb = None

    with patch.object(_handler, "_fire"):
        _handler._on_exception(exc_type, exc_value, exc_tb)

    original_hook.assert_called_once_with(exc_type, exc_value, exc_tb)


def test_enable_with_specific_mood():
    _handler.enable(mood="cringe")
    assert _handler._mood == "cringe"


def test_enable_with_custom_messages(monkeypatch):
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    custom = {"test_mood": ["Custom message here."]}
    _handler.enable(mood="test_mood", custom=custom)
    _handler._fired = False

    printed = []
    with patch("builtins.print", side_effect=lambda *a, **kw: printed.append(a)):
        _handler._fire("test")

    assert printed
    assert "Custom message here." in printed[0][0]


def test_fire_swallows_picker_exception(monkeypatch):
    # Covers handler.py lines 97-98: except Exception: return
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="comic")
    _handler._fired = False

    with patch("tantrumpy.handler._picker.pick", side_effect=RuntimeError("boom")):
        with patch("builtins.print") as mock_print:
            _handler._fire("test")  # must not raise
            mock_print.assert_not_called()


def test_on_sigint_fires_and_reraises(monkeypatch):
    # Covers handler.py lines 111-114: _on_sigint body
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="rude")
    _handler._fired = False

    with patch("signal.raise_signal") as mock_raise:
        with patch.object(_handler, "_fire") as mock_fire:
            _handler._on_sigint(signal.SIGINT, None)
            mock_fire.assert_called_once_with("SIGINT (Ctrl+C)")
            mock_raise.assert_called_once_with(signal.SIGINT)


def test_on_sigterm_fires_and_reraises(monkeypatch):
    # Covers handler.py lines 117-119: _on_sigterm body
    monkeypatch.delenv("TANTRUMPY_SILENT", raising=False)
    _handler.enable(mood="dramatic")
    _handler._fired = False

    with patch("signal.raise_signal") as mock_raise:
        with patch.object(_handler, "_fire") as mock_fire:
            _handler._on_sigterm(signal.SIGTERM, None)
            mock_fire.assert_called_once_with("SIGTERM")
            mock_raise.assert_called_once_with(signal.SIGTERM)
