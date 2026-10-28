# Keyboardo

A desktop touch-typing tutor built with Python and Tkinter, inspired by Klavaro’s short, randomized key exercises.

## Practice

Run `./bin/run.sh` with a Tk-enabled Python environment in `.venv`, or set `KEYBOARDO_PYTHON` to your interpreter. No third-party runtime packages are required.

The basic course loads one lesson per nonempty line inside the code block in `documentation/LESSONS.md`. The current six key mixes are `fj`, `dk`, `sl`, `a;`, `fdsa`, and `jkl;`. Edit the file and restart the app to change the course. Each exercise shuffles the lesson’s keys into five-character groups. Type the highlighted character, using spaces between groups and Return at each ↵. Type directly in the exercise area. Mistakes appear there in red and must be removed with Backspace. Timing starts with the first printable key; Escape returns to the main menu; Restart starts a new exercise. Results appear in a dialog after completion, where you can advance to the next lesson. A result of at least 95% accuracy marks the lesson as passed in saved progress. Text insertion lets you practise your own text.

WPM counts completed characters (including spaces), divided by five, per minute. Accuracy includes every incorrect attempt. Best results are stored locally in `~/Library/Application Support/Keyboardo/progress.json` on macOS.

## Build a macOS DMG

Font, font size, sounds, and the last selected lesson are saved automatically in `~/.config/keyboardo/config.toml`. On first launch with this location, settings from the older `~/.keyboardo_config` JSON file are migrated if present. The old file is preserved. TOML loading requires Python 3.11 or newer.

The header and app icon use `resources/logo.svg`. The accompanying PNG files and `Keyboardo.icns` are derived from that SVG; regenerate them when changing the source logo. The build bundles the resources and uses the ICNS file for the macOS app icon.

Use a stable Python release supported by PyInstaller with working Tkinter. Install PyInstaller in that environment, then run `./bin/build-dmg.sh` (set `KEYBOARDO_PYTHON` if needed). The script creates `dist/Keyboardo.app` and `dist/Keyboardo.dmg`, with an Applications shortcut for drag-to-install. Build on the target architecture; this script does not produce a universal binary.

The generated app is unsigned. Signing and notarization with an Apple Developer identity are required for a normal public macOS release.

## Tests

Run `.venv/bin/python -m unittest discover -s tests -v`. No extra test dependencies or GUI session are needed. In PyCharm, right-click `tests/test_core.py` and run its unittest tests. The suite covers lesson parsing and generation, exercise wrapping, settings validation and migration, and progress storage using temporary files.

## Source layout

`src/keyboardo/app.py` coordinates navigation and typing. Screen construction lives in `views/`, with separate files for the menu, settings, text insertion, practice, header, and results dialog. Other modules handle lesson generation (`lessons.py`), row layout (`exercise.py`), TOML preferences (`config.py`), saved results (`progress.py`), sounds (`sounds.py`), styling (`theme.py`), animated buttons (`widgets.py`), and resource paths (`resources.py`).

The existing `./bin/run.sh` and direct `app.py` launch still work. You can also run the package with `PYTHONPATH=src .venv/bin/python -m keyboardo`.
