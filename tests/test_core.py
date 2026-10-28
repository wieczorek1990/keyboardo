"""Core behavior tests; runnable with unittest, pytest, or an IDE runner."""
from collections import Counter
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

# Allow discovery and direct IDE execution without installing the application.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from keyboardo.config import load_settings, read_config, save_config
from keyboardo.exercise import layout_exercise
from keyboardo.lessons import load_lessons, make_exercise
from keyboardo.progress import load_progress, save_progress


class TemporaryFilesTestCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def write(self, name, contents):
        path = self.directory / name
        path.write_text(contents, encoding="utf-8")
        return path


class LessonsTests(TemporaryFilesTestCase):
    def test_only_nonempty_code_block_lines_define_lessons(self):
        path = self.write("lessons.md", "Ignore this\n```text\nf j\n\n d k \n```\nIgnore too\n```\na;\n```\n")
        self.assertEqual(load_lessons(path), (
            ("01 · fj", "fj", ""), ("02 · dk", "dk", ""), ("03 · a;", "a;", "")))

    def test_missing_key_mixes_raise_value_error(self):
        path = self.write("lessons.md", "No lessons\n```\n \n```\n")
        with self.assertRaisesRegex(ValueError, "No lesson key mixes"):
            load_lessons(path)

    def test_exercise_preserves_balanced_keys_and_five_character_groups(self):
        exercise = make_exercise("fj", random.Random(7))
        self.assertEqual(Counter(exercise.replace(" ", "")), {"f": 30, "j": 30})
        self.assertEqual([len(group) for group in exercise.split()], [5] * 12)

    def test_exercise_rounds_up_to_include_every_key_equally(self):
        exercise = make_exercise("abcdefg", random.Random(7))
        self.assertEqual(Counter(exercise.replace(" ", "")), dict.fromkeys("abcdefg", 9))

    def test_seeded_generation_is_repeatable(self):
        self.assertEqual(make_exercise("fjdk", random.Random(9)),
                         make_exercise("fjdk", random.Random(9)))


class ExerciseLayoutTests(unittest.TestCase):
    def test_groups_that_fit_keep_original_offsets(self):
        self.assertEqual(layout_exercise("ab cd", 7, len),
                         ("ab cd", list(range(6)), set()))

    def test_wrap_reserves_return_marker_space_and_maps_offsets(self):
        self.assertEqual(layout_exercise("ab cd", 6, len),
                         ("ab↵\ncd", [0, 1, 2, 4, 5, 6], {2}))

    def test_long_groups_are_never_split(self):
        self.assertEqual(layout_exercise("abcdef gh", 3, len),
                         ("abcdef↵\ngh", [0, 1, 2, 3, 4, 5, 6, 8, 9, 10], {6}))

    def test_trailing_newline_becomes_return_marker(self):
        self.assertEqual(layout_exercise("ab\n", 10, len),
                         ("ab↵", [0, 1, 2, 3], set()))

    def test_empty_exercise(self):
        self.assertEqual(layout_exercise("", 10, len), ("", [0], set()))


class ConfigTests(TemporaryFilesTestCase):
    def test_round_trip_and_replacement_in_nested_directory(self):
        path = self.directory / "nested/config.toml"
        settings = {"font": 'A "quoted" font \\ Ω', "font_size": 16,
                    "sounds": False, "last_lesson": 3}
        save_config(path, settings)
        self.assertEqual(load_settings(path), settings)
        settings["font_size"] = 20
        save_config(path, settings)
        self.assertEqual(load_settings(path), settings)
        self.assertEqual(list(path.parent.iterdir()), [path])

    def test_invalid_setting_types_and_ranges_are_ignored(self):
        path = self.write("config.toml", 'font = 42\nfont_size = true\nsounds = "yes"\nlast_lesson = 0\n')
        self.assertEqual(load_settings(path), {})
        for size in (9, 21):
            with self.subTest(size=size):
                path.write_text(f"font_size = {size}\n")
                self.assertEqual(load_settings(path), {})

    def test_font_size_boundaries_are_accepted(self):
        for size in (10, 20):
            with self.subTest(size=size):
                path = self.write("config.toml", f"font_size = {size}\n")
                self.assertEqual(load_settings(path), {"font_size": size})

    def test_missing_and_malformed_files_return_empty_settings(self):
        self.assertEqual(load_settings(self.directory / "missing"), {})
        path = self.write("config.toml", "not valid TOML = [")
        self.assertEqual(load_settings(path), {})

    def test_explicit_path_does_not_use_legacy_config(self):
        self.write(".keyboardo_config", '{"font_size": 16}')
        path = self.directory / "custom.toml"
        with patch("keyboardo.config.Path.home", return_value=self.directory):
            self.assertEqual(read_config(path), (path, {}, False))

    def test_legacy_settings_are_loaded_without_modifying_legacy_file(self):
        legacy = self.write(".keyboardo_config", '{"font_size": 16, "sounds": false}')
        original = legacy.read_text()
        with patch("keyboardo.config.Path.home", return_value=self.directory):
            path, settings, migrate = read_config()
        self.assertEqual(path, self.directory / ".config/keyboardo/config.toml")
        self.assertEqual(settings, {"font_size": 16, "sounds": False})
        self.assertTrue(migrate)
        self.assertEqual(legacy.read_text(), original)
        self.assertFalse(path.exists())

    def test_existing_config_takes_precedence_over_legacy(self):
        self.write(".keyboardo_config", '{"font_size": 16}')
        path = self.directory / ".config/keyboardo/config.toml"
        save_config(path, {"font": "Mono", "font_size": 12, "sounds": True})
        with patch("keyboardo.config.Path.home", return_value=self.directory):
            actual_path, settings, migrate = read_config()
        self.assertEqual(actual_path, path)
        self.assertEqual(settings["font_size"], 12)
        self.assertFalse(migrate)


class ProgressTests(TemporaryFilesTestCase):
    def test_round_trip_replaces_previous_progress_and_cleans_temporary_file(self):
        path = self.directory / "nested/progress.json"
        save_progress(path, {"old": {"accuracy": 80, "wpm": 10}})
        progress = {"fj": {"accuracy": 98.5, "wpm": 42}}
        save_progress(path, progress)
        self.assertEqual(load_progress(path), progress)
        self.assertFalse(path.with_suffix(".tmp").exists())

    def test_invalid_entries_are_filtered_without_losing_valid_results(self):
        path = self.write("progress.json", '{"good": {"accuracy": 95, "wpm": 30}, '
                          '"missing": {"accuracy": 95}, "text": {"accuracy": "95", "wpm": 30}, '
                          '"null": null}')
        self.assertEqual(load_progress(path), {"good": {"accuracy": 95, "wpm": 30}})

    def test_missing_corrupt_and_non_object_progress_are_ignored(self):
        self.assertEqual(load_progress(self.directory / "missing"), {})
        for contents in ("{broken", "[]", "null", '"text"'):
            with self.subTest(contents=contents):
                self.assertEqual(load_progress(self.write("progress.json", contents)), {})


if __name__ == "__main__":
    unittest.main()
