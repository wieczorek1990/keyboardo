"""Nonblocking macOS sound feedback with a Tk bell fallback."""
from pathlib import Path
import subprocess
import sys


class SoundPlayer:
    def __init__(self, root):
        self.root = root
        self.processes = []

    def play(self, kind, enabled):
        if not enabled:
            return
        sounds = {"error": "Basso", "space": "Tink", "newline": "Pop", "complete": "Glass"}
        sound = Path("/System/Library/Sounds") / f"{sounds[kind]}.aiff"
        if sys.platform == "darwin" and sound.is_file():
            self.processes = [process for process in self.processes if process.poll() is None]
            try:
                self.processes.append(subprocess.Popen(
                    ["/usr/bin/afplay", str(sound)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
                return
            except OSError:
                pass
        self.root.bell()
