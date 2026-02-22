"""
tantrumpy demo — see all moods and exit triggers in action.

Usage:
    python examples/demo.py                  # random mood, sys.exit trigger
    python examples/demo.py frustrated       # specific mood
    python examples/demo.py --crash          # trigger unhandled exception
    python examples/demo.py --silent         # no output (TANTRUMPY_SILENT=1)
"""
import os
import sys

# Allow running from project root without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import tantrumpy

MOODS = ["frustrated", "rude", "comic", "cringe", "philosophy", "dramatic"]


def show_all_moods():
    """Print one sample message from each built-in mood (no hooks needed)."""
    from tantrumpy.picker import pick, get_emoji
    from tantrumpy.colors import colorize

    print("\n=== tantrumpy — mood preview ===\n")
    for mood in MOODS:
        emoji = get_emoji(mood)
        msg = pick(mood)
        print(f"  {emoji} [{mood}] {colorize(msg, mood)}")
    print()


def main():
    args = sys.argv[1:]

    if "--preview" in args:
        show_all_moods()
        return

    if "--crash" in args:
        mood = next((a for a in args if a in MOODS), "rude")
        print(f"\n[demo] Simulating a crash with mood='{mood}'...")
        tantrumpy.enable(mood=mood, verbose=True)
        raise RuntimeError("Simulated crash for demo purposes.")

    if "--silent" in args:
        os.environ["TANTRUMPY_SILENT"] = "1"
        tantrumpy.enable()
        print("[demo] TANTRUMPY_SILENT=1 — no tantrum will be printed on exit.")
        sys.exit(0)

    # Default: pick mood from args or use random
    mood = next((a for a in args if a in MOODS), "random")
    print(f"\n[demo] Running with mood='{mood}'. Exit to see the tantrum...\n")
    tantrumpy.enable(mood=mood, verbose=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
