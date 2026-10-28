"""Practice screen presentation."""
import tkinter as tk
from tkinter import ttk

from ..theme import BACKGROUND, SURFACE, EMPHASIS, PRIMARY, ACCENT
from ..widgets import AnimatedButton
from ..lessons import LESSONS


def build_practice(app):
    root = app.root
    app.course = tk.Frame(root, bg=BACKGROUND)
    app.practice_canvas = tk.Canvas(app.course, bg=BACKGROUND, highlightthickness=0, yscrollincrement=20)
    practice_scrollbar = ttk.Scrollbar(app.course, orient="vertical", command=app.practice_canvas.yview)
    app.practice_canvas.configure(yscrollcommand=practice_scrollbar.set)
    practice_scrollbar.pack(side="right", fill="y")
    app.practice_canvas.pack(side="left", fill="both", expand=True)
    body = tk.Frame(app.practice_canvas, bg=BACKGROUND, padx=28, pady=12)
    practice_window = app.practice_canvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>", lambda event: app.practice_canvas.configure(scrollregion=app.practice_canvas.bbox("all")))
    app.practice_canvas.bind("<Configure>", lambda event: app.practice_canvas.itemconfigure(practice_window, width=event.width))
    root.bind("<MouseWheel>", app.scroll_practice, add="+")
    root.bind("<Button-4>", app.scroll_practice, add="+")
    root.bind("<Button-5>", app.scroll_practice, add="+")
    navigation = tk.Frame(body, bg=BACKGROUND)
    navigation.pack(fill="x", pady=(0, 20))
    AnimatedButton(navigation, text="← Main menu", command=app.show_menu).pack(side="left")
    AnimatedButton(navigation, text="Restart", command=app.start_lesson).pack(side="left", padx=(12, 0))
    selector = tk.Frame(navigation, bg=BACKGROUND)
    app.selector = selector
    selector.pack(side="right")
    tk.Label(selector, text="Lesson", bg=BACKGROUND, fg=EMPHASIS, font=app.fonts["selector"]).pack(side="left", padx=(0, 8))
    app.lesson_number = tk.StringVar(value="1")
    tk.Label(selector, textvariable=app.lesson_number, width=2, bg=BACKGROUND, fg=EMPHASIS, font=app.fonts["selector"]).pack(side="left", padx=(0, 8))
    app.previous_arrow = AnimatedButton(selector, text="◀", style="LessonArrow.TButton", width=0, command=lambda: app.change_lesson(-1))
    app.previous_arrow.pack(side="left")
    app.next_arrow = AnimatedButton(selector, text="▶", style="LessonArrow.TButton", width=0, command=lambda: app.change_lesson(1))
    app.next_arrow.pack(side="left", padx=(4, 0))
    tk.Label(selector, text=str(len(LESSONS)), bg=BACKGROUND, fg=EMPHASIS, font=app.fonts["selector"]).pack(side="left", padx=(8, 0))
    main = tk.Frame(body, bg=BACKGROUND)
    main.pack(fill="both", expand=True)
    app.title = tk.Label(main, font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS, anchor="w")
    app.title.pack(fill="x", pady=(0, 18))
    app.tip = tk.Label(main, font=app.fonts["body"], wraplength=540, justify="left", bg=BACKGROUND, fg=PRIMARY)
    app.text = tk.Text(main, height=4, wrap="none", font=app.fonts["typing"], bg=SURFACE, fg=PRIMARY, relief="flat", padx=20, pady=20, takefocus=True, cursor="arrow")
    app.text.pack(fill="x")
    app.text.bind("<Configure>", app.resize_exercise)
    app.text.tag_configure("correct", foreground=ACCENT)
    app.text.tag_configure("current", background=BACKGROUND, foreground=EMPHASIS, underline=True)
    app.text.tag_configure("error", foreground="#b34747", underline=True)
    app.text.configure(state="disabled")
    app.text.bind("<KeyPress>", app.type_key)
    app.message = tk.Label(main, font=app.fonts["small"], bg=BACKGROUND, fg=PRIMARY, wraplength=540, justify="left")
