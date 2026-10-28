"""Application navigation and practice interaction."""
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import font as tkfont

# Keep direct execution and PyInstaller's script entry point working.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from keyboardo.config import read_config, save_config
from keyboardo.exercise import layout_exercise
from keyboardo.lessons import LESSONS, make_exercise
from keyboardo.progress import load_progress, progress_path, save_progress
from keyboardo.sounds import SoundPlayer
from keyboardo.theme import BACKGROUND, FONT_BODY, configure_theme
from keyboardo.widgets import AnimatedButton
from keyboardo.windowing import center_on_desktop
from keyboardo.views.header import build_header
from keyboardo.views.menu import build_menu
from keyboardo.views.settings import align_settings_controls, build_settings
from keyboardo.views.insertion import build_insertion
from keyboardo.views.practice import build_practice
from keyboardo.views.results import show_results


class Keyboardo:
    def __init__(self, root, config_path=None):
        self.root = root
        self.config_path, settings, migrate_settings = read_config(config_path)
        self.loading_settings = True
        self.path = progress_path()
        self.progress = load_progress(self.path)
        self.lesson = min(settings.get("last_lesson", 1), len(LESSONS)) - 1
        self.in_course = False
        self.custom_text = None
        self.sound_player = SoundPlayer(root)
        root.title("Keyboardo")
        root.geometry("1000x720")
        root.minsize(820, 620)
        root.configure(bg=BACKGROUND)
        self.fonts, self.base_font_sizes = configure_theme(root)
        build_header(self)
        build_menu(self)
        build_settings(self, settings)
        build_insertion(self)
        build_practice(self)
        root.bind("<Escape>", self.escape_navigation)
        root.bind("<less>", self.switch_lesson_key)
        root.bind("<greater>", self.switch_lesson_key)
        root.bind("<BackSpace>", lambda event: None if event.widget is self.source_text else self.backspace_navigation(event))
        self.show_menu()
        if settings.get("font") in self.font_selector.cget("values"):
            self.select_font()
        self.select_font_size()
        self.loading_settings = False
        if migrate_settings:
            self.save_settings()
        root.after_idle(self.center_window)

    def center_window(self):
        center_on_desktop(self.root)

    def save_settings(self):
        if self.loading_settings:
            return
        settings = {"font": self.font_choice.get(), "font_size": int(self.font_size.get()),
                    "sounds": self.sounds_enabled.get(), "last_lesson": self.lesson + 1}
        try:
            save_config(self.config_path, settings)
            self.settings_message.configure(text="")
        except OSError:
            self.settings_message.configure(text="Could not save settings. Changes apply for this session.")

    def refresh_button_sizes(self):
        self.root.update_idletasks()
        def visit(widget):
            for child in widget.winfo_children():
                if isinstance(child, AnimatedButton):
                    child.refresh_size()
                visit(child)
        visit(self.root)

    def select_font(self, _event=None):
        family = self.font_choice.get()
        for font in self.fonts.values():
            font.configure(family=family)
        align_settings_controls(self)
        self.refresh_button_sizes()
        self.fit_menu_window()
        if self.in_course and hasattr(self, "target"):
            self.render()
        self.save_settings()

    def show_menu(self):
        self.in_course = False
        self.course.pack_forget()
        self.insertion.pack_forget()
        self.settings.pack_forget()
        self.menu.pack(fill="both", expand=True)
        self.course_button.focus_set()

    def show_settings(self):
        self.show_menu()
        self.menu.pack_forget()
        self.settings.pack(fill="both", expand=True)
        self.font_selector.focus_set()

    def backspace_navigation(self, event):
        if event.widget is self.source_text and self.source_text.get("1.0", "end-1c"):
            return
        if self.in_course or self.insertion.winfo_ismapped() or self.settings.winfo_ismapped():
            self.show_menu()
            return "break"

    def select_font_size(self):
        scale = int(self.font_size.get()) / FONT_BODY[1]
        for role, font in self.fonts.items():
            font.configure(size=round(self.base_font_sizes[role] * scale))
        align_settings_controls(self)
        self.refresh_button_sizes()
        self.fit_menu_window()
        if self.in_course and hasattr(self, "target"):
            self.render()
        self.save_settings()

    def fit_menu_window(self):
        """Reserve enough space for the selected font's actual menu metrics."""
        self.root.update_idletasks()
        scale = max(1, self.fonts["body"].cget("size") / FONT_BODY[1])
        width = max(round(820 * scale), self.menu.winfo_reqwidth())
        height = max(round(620 * scale), self.header.winfo_reqheight() + self.menu.winfo_reqheight())
        self.root.minsize(width, height)

    def play_feedback(self, kind):
        self.sound_player.play(kind, self.sounds_enabled.get())

    def move_menu(self, index, direction):
        self.menu_buttons[(index + direction) % len(self.menu_buttons)].focus_set()
        return "break"

    def activate_menu(self, button):
        button.invoke()
        return "break"

    def show_course(self):
        self.custom_text = None
        self.menu.pack_forget()
        self.insertion.pack_forget()
        self.selector.pack(side="right")
        self.course.pack(fill="both", expand=True)
        self.in_course = True
        self.start_lesson()

    def show_text_insertion(self):
        self.show_menu()
        self.menu.pack_forget()
        self.insertion.pack(fill="both", expand=True)
        self.insertion_message.configure(text="")
        self.source_text.focus_set()

    def start_custom_text(self):
        text = " ".join(self.source_text.get("1.0", "end-1c").split())
        if not text:
            self.insertion_message.configure(text="Enter some text before starting.")
            self.source_text.focus_set()
            return
        self.custom_text = text
        self.insertion.pack_forget()
        self.selector.pack_forget()
        self.course.pack(fill="both", expand=True)
        self.in_course = True
        self.start_lesson()

    def escape_navigation(self, _event=None):
        if self.in_course or self.settings.winfo_ismapped() or self.insertion.winfo_ismapped():
            self.show_menu()
        elif self.menu.winfo_ismapped():
            self.root.destroy()
        return "break"

    def scroll_practice(self, event):
        if not self.in_course or isinstance(event.widget, tk.Text):
            return
        widget = event.widget
        while widget is not None and widget is not self.course:
            widget = widget.master
        if widget is None:
            return
        if event.num in (4, 5):
            units = -1 if event.num == 4 else 1
        else:
            units = -int(event.delta) if sys.platform == "darwin" else -int(event.delta / 120)
        self.practice_canvas.yview_scroll(units, "units")
        return "break"

    def refresh_lessons(self):
        self.lesson_number.set(str(self.lesson + 1))
        self.previous_arrow.configure(state="normal" if self.lesson > 0 else "disabled")
        self.next_arrow.configure(state="normal" if self.custom_text is None and self.lesson < len(LESSONS) - 1 else "disabled")

    def change_lesson(self, offset):
        selected = self.lesson + offset
        if self.in_course and self.custom_text is None and 0 <= selected < len(LESSONS):
            self.lesson = selected
            self.start_lesson()

    def switch_lesson_key(self, event):
        if self.in_course and self.custom_text is None and self.root.grab_current() is None:
            self.change_lesson(-1 if event.char == "<" else 1)
            return "break"

    def start_lesson(self):
        if self.custom_text is None:
            name, keys, tip = LESSONS[self.lesson]
            self.target = make_exercise(keys) + "\n"
        else:
            name, keys, tip = "Your text", "", "Practise your own text. Press Return at each ↵."
            self.target = self.custom_text + "\n"
        self.title.configure(text=name)
        self.tip.configure(text=tip)
        if tip:
            self.tip.pack(anchor="w", pady=(0, 18), before=self.text)
        else:
            self.tip.pack_forget()
        self.reset_practice()
        if self.custom_text is None:
            self.save_settings()

    def edit_practice(self):
        if not self.in_course:
            return
        if self.custom_text is None:
            self.source_text.delete("1.0", "end")
            self.source_text.insert("1.0", self.target.rstrip("\n"))
        self.show_text_insertion()

    def reset_practice(self):
        if not self.in_course:
            return
        self.finished = False
        self.position = self.attempts = self.errors = 0
        self.input_errors = ""
        self.started = None
        self.message.pack_forget()
        self.refresh_lessons()
        self.render()
        self.practice_canvas.yview_moveto(0)
        self.text.focus_set()
        self.root.after_idle(self.focus_practice_input)

    def focus_practice_input(self):
        if self.in_course and not self.finished and self.text.winfo_viewable():
            self.text.focus_set()

    def resize_exercise(self, _event):
        if self.in_course and hasattr(self, "target"):
            self.render()

    def layout_exercise(self):
        font = tkfont.Font(font=self.text.cget("font"))
        width = max(1, self.text.winfo_width() - 2 * int(self.text.cget("padx")))
        display, self.display_offsets, self.row_breaks = layout_exercise(self.target, width, font.measure)
        return display

    def render(self):
        display = self.layout_exercise()
        current = self.display_offsets[self.position]
        mistakes = self.input_errors.replace(" ", "␣")
        display = display[:current] + mistakes + display[current:]
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", display)
        self.text.tag_add("correct", "1.0", f"1.0+{current}c")
        self.text.tag_add("error", f"1.0+{current}c", f"1.0+{current + len(mistakes)}c")
        current += len(mistakes)
        if not self.finished:
            self.text.tag_add("current", f"1.0+{current}c", f"1.0+{current + 1}c")
        self.text.see(f"1.0+{current}c")
        self.text.configure(state="disabled")

    def type_key(self, event):
        if event.keysym == "Escape":
            return self.escape_navigation(event)
        if event.char in ("<", ">") and self.custom_text is None:
            return self.switch_lesson_key(event)
        if not self.in_course:
            return "break"
        if event.keysym == "BackSpace":
            if self.input_errors:
                self.input_errors = self.input_errors[:-1]
                self.render()
            else:
                self.show_menu()
            return "break"
        if self.finished:
            return "break"
        # Leave system shortcuts alone; block paste so it cannot complete a lesson.
        if event.state & 0xC:
            return "break"
        char = "\n" if event.keysym in ("Return", "KP_Enter") else event.char
        if not char or (not char.isprintable() and char != "\n"):
            return "break"
        if self.started is None:
            self.started = time.monotonic()
        self.attempts += 1
        expected = "\n" if self.position in self.row_breaks else self.target[self.position]
        if char == expected and not self.input_errors:
            self.position += 1
            if char in (" ", "\n"):
                if self.position < len(self.target):
                    self.play_feedback("space" if char == " " else "newline")
        else:
            self.errors += 1
            self.play_feedback("error")
            self.input_errors += "↵" if char == "\n" else char
        self.finished = self.position == len(self.target)
        self.render()
        if self.finished:
            self.complete()
        return "break"

    def metrics(self):
        elapsed = max(time.monotonic() - self.started, 0.1) if self.started else 0
        accuracy = (self.attempts - self.errors) / self.attempts * 100 if self.attempts else 100
        wpm = self.position / 5 / (elapsed / 60) if elapsed else 0
        return elapsed, accuracy, wpm

    def complete(self):
        self.play_feedback("complete")
        elapsed, accuracy, wpm = self.metrics()
        if self.custom_text is not None:
            show_results(self, elapsed, accuracy, wpm)
            return
        lesson_key = LESSONS[self.lesson][1]
        previous = self.progress.get(lesson_key, {})
        if (accuracy, wpm) > (previous.get("accuracy", -1), previous.get("wpm", -1)):
            self.progress[lesson_key] = {"accuracy": accuracy, "wpm": wpm}
        try:
            save_progress(self.path, self.progress)
        except OSError:
            self.message.configure(text="Progress could not be saved.")
            self.message.pack(anchor="w", pady=(12, 0))
        self.refresh_lessons()
        show_results(self, elapsed, accuracy, wpm)

    def next_lesson(self):
        if self.in_course and self.finished and self.custom_text is None and self.lesson < len(LESSONS) - 1:
            self.lesson += 1
            self.refresh_lessons()
            self.start_lesson()


def main():
    root = tk.Tk()
    Keyboardo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
