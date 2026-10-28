"""Menu screen presentation."""
import tkinter as tk

from ..theme import BACKGROUND, EMPHASIS, PRIMARY
from ..widgets import AnimatedButton


def build_menu(app):
    root = app.root
    app.menu = tk.Frame(root, bg=BACKGROUND, padx=28, pady=24)
    app.menu.grid_rowconfigure(0, weight=1)
    app.menu.grid_columnconfigure(0, weight=1)
    content = tk.Frame(app.menu, bg=BACKGROUND)
    content.grid(row=0, column=0)
    heading = tk.Label(content, text="Welcome to Keyboardo", font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS, justify="center", anchor="center")
    heading.pack(fill="x", pady=(0, 12))
    description = tk.Label(content, text="Choose a course and build your typing confidence.", font=app.fonts["body"], bg=BACKGROUND, fg=PRIMARY, justify="center", anchor="center")
    description.pack(fill="x", pady=(0, 28))
    app.course_button = AnimatedButton(content, font=app.fonts["body"], text="Basic course →", width=0, command=app.show_course)
    app.course_button.pack(fill="x", pady=8)
    insertion_button = AnimatedButton(content, font=app.fonts["body"], text="Text insertion →", width=0, command=app.show_text_insertion)
    insertion_button.pack(fill="x", pady=8)
    settings_button = AnimatedButton(content, font=app.fonts["body"], text="Settings →", width=0, command=app.show_settings)
    settings_button.pack(fill="x", pady=8)
    exit_button = AnimatedButton(content, font=app.fonts["body"], text="Exit", width=0, command=root.destroy)
    exit_button.pack(fill="x", pady=8)

    def fit_text(event):
        available_width = max(1, event.width - 2 * int(app.menu.cget("padx")))
        heading.configure(wraplength=available_width)
        description.configure(wraplength=available_width)

    app.menu.bind("<Configure>", fit_text)
    app.menu_buttons = [app.course_button, insertion_button, settings_button, exit_button]
    for index, button in enumerate(app.menu_buttons):
        button.bind("<Up>", lambda event, i=index: app.move_menu(i, -1))
        button.bind("<Down>", lambda event, i=index: app.move_menu(i, 1))
        button.bind("<Return>", lambda event, selected=button: app.activate_menu(selected))
        button.bind("<KP_Enter>", lambda event, selected=button: app.activate_menu(selected))
