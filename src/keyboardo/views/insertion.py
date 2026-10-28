"""Insertion screen presentation."""
import tkinter as tk

from ..theme import BACKGROUND, SURFACE, EMPHASIS, PRIMARY
from ..widgets import AnimatedButton


def build_insertion(app):
    root = app.root
    app.insertion = tk.Frame(root, bg=BACKGROUND, padx=28, pady=12)
    AnimatedButton(app.insertion, text="← Main menu", command=app.show_menu).pack(anchor="w", pady=(0, 20))
    tk.Label(app.insertion, text="Text insertion", font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS).pack(anchor="w")
    tk.Label(app.insertion, text="Type or paste the text you want to practise.", font=app.fonts["body"], bg=BACKGROUND, fg=PRIMARY).pack(anchor="w", pady=(10, 16))
    app.source_text = tk.Text(app.insertion, height=10, wrap="word", font=app.fonts["body"], bg=SURFACE, fg=EMPHASIS, insertbackground=EMPHASIS, relief="flat", padx=16, pady=16, undo=True)
    app.source_text.pack(fill="both", expand=True)
    app.source_text.bind("<BackSpace>", app.backspace_navigation)
    app.insertion_message = tk.Label(app.insertion, text="", font=app.fonts["small"], bg=BACKGROUND, fg=EMPHASIS)
    app.insertion_message.pack(anchor="w", pady=10)
    AnimatedButton(app.insertion, text="Start practice →", command=app.start_custom_text).pack(anchor="e", pady=(0, 16))
