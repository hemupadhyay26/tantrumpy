"""
TantrumHandler — wires up all exit hooks and fires the tantrum message.

Hooks registered:
  - signal.SIGINT  (Ctrl+C)
  - signal.SIGTERM (kill signal)
  - atexit         (sys.exit / normal end)
  - sys.excepthook (unhandled exceptions)
"""
import atexit
import os
import signal
import sys
import types
from typing import Any, Callable, Dict, List, Optional

from tantrumpy import picker as _picker
from tantrumpy.colors import colorize


class TantrumHandler:
    """Singleton that manages all exit hook registrations."""

    def __init__(self) -> None:
        self._active = False
        self._fired = False
        self._mood = "random"
        self._verbose = False
        self._custom: Optional[Dict[str, List[str]]] = None

        # Saved originals for clean restore on disable()
        self._orig_sigint: Any = signal.SIG_DFL
        self._orig_sigterm: Any = signal.SIG_DFL
        self._orig_excepthook: Callable[..., None] = sys.__excepthook__

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def enable(
        self,
        mood: str = "random",
        verbose: bool = False,
        custom: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """Register all exit hooks."""
        self._mood = mood
        self._verbose = verbose
        self._custom = custom
        self._fired = False
        self._active = True

        # Save originals before replacing
        self._orig_sigint = signal.getsignal(signal.SIGINT)
        self._orig_sigterm = signal.getsignal(signal.SIGTERM)
        self._orig_excepthook = sys.excepthook

        signal.signal(signal.SIGINT, self._on_sigint)
        signal.signal(signal.SIGTERM, self._on_sigterm)
        sys.excepthook = self._on_exception
        atexit.register(self._on_atexit)

    def disable(self) -> None:
        """Restore original handlers and unhook everything."""
        if not self._active:
            return

        signal.signal(signal.SIGINT, self._orig_sigint)
        signal.signal(signal.SIGTERM, self._orig_sigterm)
        sys.excepthook = self._orig_excepthook

        self._active = False
        self._fired = False

    # ------------------------------------------------------------------
    # Internal — fire tantrum
    # ------------------------------------------------------------------

    def _fire(self, trigger: str) -> None:
        """Pick and print the exit message. Fires only once per session."""
        if self._fired:
            return
        self._fired = True

        if os.environ.get("TANTRUMPY_SILENT"):
            return

        # Resolve actual mood (handles "random")
        try:
            resolved_mood = (
                self._mood
                if self._mood != "random"
                else __import__("random").choice(_picker.all_moods())
            )
            message = _picker.pick(resolved_mood, self._custom)
            emoji = _picker.get_emoji(resolved_mood)
        except Exception:
            return  # never crash the app just to print a tantrum

        line = f"{emoji} {colorize(message, resolved_mood)}"
        if self._verbose:
            line += f"  \033[2m[exit via: {trigger}]\033[0m"

        print(f"\n{line}", file=sys.stderr)

    # ------------------------------------------------------------------
    # Hook handlers
    # ------------------------------------------------------------------

    def _on_sigint(self, signum: int, frame: Optional[types.FrameType]) -> None:
        self._fire("SIGINT (Ctrl+C)")
        # Restore original and re-raise so the process exits normally
        signal.signal(signal.SIGINT, self._orig_sigint)
        signal.raise_signal(signal.SIGINT)

    def _on_sigterm(self, signum: int, frame: Optional[types.FrameType]) -> None:
        self._fire("SIGTERM")
        signal.signal(signal.SIGTERM, self._orig_sigterm)
        signal.raise_signal(signal.SIGTERM)

    def _on_atexit(self) -> None:
        self._fire("sys.exit / normal exit")

    def _on_exception(
        self,
        exc_type: type,
        exc_value: BaseException,
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        # Print the original traceback first
        self._orig_excepthook(exc_type, exc_value, exc_tb)
        # Then fire the tantrum below it
        self._fire(f"exception: {exc_type.__name__}")


# Module-level singleton
_handler = TantrumHandler()
