"""
ANSI color support for tantrumpy.
Colored by default — falls back to plain text when terminal doesn't support it.
"""
import os
import sys
from typing import Dict

# ANSI codes per mood
MOOD_COLORS: Dict[str, str] = {
    "frustrated": "\033[31m",    # Red
    "rude":       "\033[35m",    # Magenta
    "comic":      "\033[36m",    # Cyan
    "cringe":     "\033[33m",    # Yellow
    "philosophy": "\033[34m",    # Blue
    "dramatic":   "\033[91m",    # Bright Red
}

RESET = "\033[0m"


def supports_color() -> bool:
    """Return True if stderr supports ANSI color codes."""
    if not hasattr(sys.stderr, "isatty") or not sys.stderr.isatty():
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    # Windows: allow if running in Windows Terminal or ConEmu (ANSI-capable)
    if os.name == "nt":
        return bool(
            os.environ.get("WT_SESSION")
            or os.environ.get("ANSICON")
            or os.environ.get("ConEmuANSI") == "ON"
        )
    return True


def colorize(message: str, mood: str) -> str:
    """Wrap message in the mood's ANSI color, or return plain if not supported."""
    if not supports_color():
        return message
    color = MOOD_COLORS.get(mood, "")
    if not color:
        return message
    return f"{color}{message}{RESET}"
