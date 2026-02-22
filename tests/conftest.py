"""Shared fixtures for tantrumpy tests."""

import pytest

from tantrumpy import picker
from tantrumpy.handler import _handler


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all global state before each test."""
    picker.reset()
    _handler.disable()
    _handler._fired = False
    yield
    _handler.disable()
    _handler._fired = False
    picker.reset()
