"""Asset locations for source and packaged runs."""
from pathlib import Path
import sys


def data_path(name):
    """Locate bundled assets both in a checkout and in a PyInstaller app."""
    base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).resolve().parents[2]
    return base / name


def resource_path(name):
    return data_path(Path("resources") / name)
