"""Shared fixtures for tantrumpy tests."""

import pytest

import tantrumpy
from tantrumpy import picker
from tantrumpy.handler import _handler


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all global state before each test."""
    picker.reset()
    _handler.disable()
    _handler._fired = False
    tantrumpy._custom_banks.clear()
    yield
    _handler.disable()
    _handler._fired = False
    picker.reset()
    tantrumpy._custom_banks.clear()
