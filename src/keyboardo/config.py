"""TOML preferences and migration from the original JSON config."""
import json
from pathlib import Path
import tempfile
import tomllib


def load_settings(path, legacy=False):
    try:
        contents = path.read_text(encoding="utf-8")
        data = json.loads(contents) if legacy else tomllib.loads(contents)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    settings = {}
    if isinstance(data.get("font"), str):
        settings["font"] = data["font"]
    if type(data.get("font_size")) is int and 10 <= data["font_size"] <= 20:
        settings["font_size"] = data["font_size"]
    if type(data.get("sounds")) is bool:
        settings["sounds"] = data["sounds"]
    if type(data.get("last_lesson")) is int and data["last_lesson"] >= 1:
        settings["last_lesson"] = data["last_lesson"]
    return settings


def read_config(config_path=None):
    path = Path(config_path) if config_path is not None else Path.home() / ".config/keyboardo/config.toml"
    settings = load_settings(path)
    migrate = config_path is None and not path.exists()
    if migrate:
        settings = load_settings(Path.home() / ".keyboardo_config", legacy=True)
        migrate = bool(settings)
    return path, settings, migrate


def save_config(path, settings):
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".config-", delete=False) as file:
            temporary = Path(file.name)
            file.write(f"font = {json.dumps(settings['font'], ensure_ascii=False)}\n")
            file.write(f"font_size = {settings['font_size']}\n")
            file.write(f"sounds = {str(settings['sounds']).lower()}\n")
            file.write(f"last_lesson = {settings.get('last_lesson', 1)}\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
