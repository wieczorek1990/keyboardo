"""Read and save the learner's best lesson results."""
import json
from pathlib import Path
import sys


def progress_path():
    base = (Path.home() / "Library/Application Support" if sys.platform == "darwin"
            else Path.home() / ".local/share")
    return base / "Keyboardo/progress.json"


def load_progress(path):
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            return {}
        return {key: value for key, value in data.items()
                if isinstance(value, dict)
                and isinstance(value.get("accuracy"), (int, float))
                and isinstance(value.get("wpm"), (int, float))}
    except (OSError, ValueError):
        return {}


def save_progress(path, progress):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(progress, indent=2))
    temporary.replace(path)
