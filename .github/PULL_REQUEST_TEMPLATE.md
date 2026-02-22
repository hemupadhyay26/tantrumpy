## What does this PR do?

<!-- A clear, one-paragraph description of the change and why it was made. -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no behavior change)
- [ ] New mood or messages
- [ ] Docs / README update
- [ ] CI / tooling change

## Related issue

<!-- Closes #<issue-number>, or "N/A" -->

## Changes made

<!--
List the key files changed and what was done in each.
Example:
- `src/tantrumpy/messages.py` — added 10 new "sarcastic" mood messages
- `tests/test_messages.py` — added integrity tests for sarcastic mood
-->

## Checklist

- [ ] I ran `uv run pytest tests/` and all tests pass
- [ ] Coverage is still >= 80% (`pytest --cov` shows no regression)
- [ ] I ran `uv run ruff check src/tantrumpy tests/` — no lint errors
- [ ] I ran `uv run ruff format src/tantrumpy tests/` — code is formatted
- [ ] New behavior is covered by tests
- [ ] I did not add any runtime dependencies (tantrumpy is zero-dependency)

## Adding a new mood? (optional)

If this PR adds a new mood, confirm:

- [ ] At least 15 messages in the new mood's bank
- [ ] Emoji defined in `MOODS` entry
- [ ] ANSI color added to `MOOD_COLORS` in `colors.py`
- [ ] Mood mentioned in `README.md` mood table
