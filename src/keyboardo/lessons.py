"""Basic-course lessons and randomized exercise generation."""
import random
from pathlib import Path

from .resources import data_path


def load_lessons(path=None):
    """Each nonempty line inside a Markdown code block defines one key mix."""
    path = Path(path) if path is not None else data_path("documentation/LESSONS.md")
    lessons = []
    in_block = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_block = not in_block
            continue
        if not in_block:
            continue
        keys = "".join(line.split())
        if keys:
            lessons.append((f"{len(lessons) + 1:02d} · {keys}", keys, ""))
    if not lessons:
        raise ValueError(f"No lesson key mixes found in {path}")
    return tuple(lessons)


LESSONS = load_lessons()


def make_exercise(keys, rng=None):
    """Use every lesson key, then shuffle into short practice groups."""
    rng = rng or random.Random()
    characters = list(keys) * max(1, (60 + len(keys) - 1) // len(keys))
    rng.shuffle(characters)
    characters = "".join(characters)
    return " ".join(characters[i:i + 5] for i in range(0, len(characters), 5))
