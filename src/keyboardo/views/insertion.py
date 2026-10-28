"""Insertion screen presentation."""
import tkinter as tk
from tkinter import ttk

from ..theme import BACKGROUND, SURFACE, EMPHASIS, PRIMARY
from ..widgets import AnimatedButton


def build_insertion(app):
    root = app.root
    app.insertion = tk.Frame(root, bg=BACKGROUND, padx=28, pady=12)
    AnimatedButton(app.insertion, text="← Main menu", command=app.show_menu).pack(anchor="w", pady=(0, 20))
    tk.Label(app.insertion, text="Text insertion", font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS).pack(anchor="w")
    tk.Label(app.insertion, text="Type or paste the text you want to practise.", font=app.fonts["body"], bg=BACKGROUND, fg=PRIMARY).pack(anchor="w", pady=(10, 16))
    # Reserve the action area before giving the editor the remaining height.
    footer = tk.Frame(app.insertion, bg=BACKGROUND)
    footer.pack(side="bottom", fill="x", pady=(12, 0))
    app.start_practice_button = AnimatedButton(footer, text="Start practice →", command=app.start_custom_text)
    app.start_practice_button.pack(side="right")
    app.insertion_message = tk.Label(footer, text="", font=app.fonts["small"], bg=BACKGROUND, fg=EMPHASIS, wraplength=360, justify="left")
    app.insertion_message.pack(side="left", fill="x", expand=True, padx=(0, 16))

    editor = tk.Frame(app.insertion, bg=BACKGROUND)
    editor.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(editor, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    app.source_text = tk.Text(editor, height=10, wrap="word", font=app.fonts["body"], bg=SURFACE, fg=EMPHASIS, insertbackground=EMPHASIS, relief="flat", padx=16, pady=16, undo=True, yscrollcommand=scrollbar.set)
    app.source_text.pack(side="left", fill="both", expand=True)
    scrollbar.configure(command=app.source_text.yview)
    app.source_text.bind("<BackSpace>", app.backspace_navigation)
    app.source_text.bind("<Escape>", app.escape_navigation)
