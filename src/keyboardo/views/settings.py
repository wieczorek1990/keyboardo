"""Settings screen presentation."""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from ..theme import BACKGROUND, EMPHASIS, FONT_BODY
from ..widgets import AnimatedButton


def build_settings(app, settings):
    root = app.root
    app.settings = tk.Frame(root, bg=BACKGROUND, padx=28, pady=12)
    AnimatedButton(app.settings, text="← Main menu", command=app.show_menu).pack(anchor="w", pady=(0, 20))
    tk.Label(app.settings, text="Settings", font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS).pack(anchor="w", pady=(0, 24))
    font_row = tk.Frame(app.settings, bg=BACKGROUND)
    font_row.pack(anchor="w", pady=(0, 20))
    tk.Label(font_row, text="Font", font=app.fonts["body"], bg=BACKGROUND, fg=EMPHASIS).pack(side="left", padx=(0, 10))
    families = sorted({family for family in tkfont.families(root) if not family.startswith("@")}, key=str.casefold)
    saved_font = settings.get("font")
    app.font_choice = tk.StringVar(value=saved_font if saved_font in families else "Helvetica")
    app.font_selector = ttk.Combobox(font_row, textvariable=app.font_choice, values=families, state="readonly", width=26, font=app.fonts["body"])
    app.font_selector.pack(side="left")
    app.font_selector.bind("<<ComboboxSelected>>", app.select_font)
    size_row = tk.Frame(app.settings, bg=BACKGROUND)
    size_row.pack(anchor="w", pady=(0, 20))
    tk.Label(size_row, text="Font size", font=app.fonts["body"], bg=BACKGROUND, fg=EMPHASIS).pack(side="left", padx=(0, 10))
    app.font_size = tk.StringVar(value=str(settings.get("font_size", FONT_BODY[1])))
    app.size_selector = ttk.Spinbox(size_row, from_=10, to=20, textvariable=app.font_size, width=4, state="readonly", font=app.fonts["body"], command=app.select_font_size)
    app.size_selector.pack(side="left")
    tk.Label(size_row, text="pt", font=app.fonts["body"], bg=BACKGROUND, fg=EMPHASIS).pack(side="left", padx=(8, 0))
    sound_row = tk.Frame(app.settings, bg=BACKGROUND)
    sound_row.pack(anchor="w")
    tk.Label(sound_row, text="Sounds", font=app.fonts["body"], bg=BACKGROUND, fg=EMPHASIS).pack(side="left", padx=(0, 10))
    app.sounds_enabled = tk.BooleanVar(value=settings.get("sounds", False))
    ttk.Checkbutton(sound_row, text="Mistakes, spaces, new lines and completion", variable=app.sounds_enabled, command=app.save_settings).pack(side="left")
    app.settings_message = tk.Label(app.settings, text="", font=app.fonts["small"], bg=BACKGROUND, fg=EMPHASIS)
    app.settings_message.pack(anchor="w", pady=(20, 0))

    def exit_settings(_event):
        app.show_menu()
        return "break"

    def bind_backspace(widget):
        widget.bind("<BackSpace>", exit_settings)
        for child in widget.winfo_children():
            bind_backspace(child)

    bind_backspace(app.settings)
