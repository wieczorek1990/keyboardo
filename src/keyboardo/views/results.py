"""Results screen presentation."""
import tkinter as tk

from ..theme import BACKGROUND, EMPHASIS, PRIMARY
from ..widgets import AnimatedButton
from ..lessons import LESSONS


def show_results(app, elapsed, accuracy, wpm):
    dialog = tk.Toplevel(app.root)
    dialog.withdraw()
    dialog.title("Results")
    dialog.configure(bg=BACKGROUND)
    dialog.transient(app.root)
    dialog.resizable(False, False)
    content = tk.Frame(dialog, bg=BACKGROUND, padx=28, pady=24)
    content.pack(fill="both", expand=True)
    tk.Label(content, text="Results", font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS).pack(anchor="w", pady=(0, 16))
    for label, value in (("Accuracy", f"{accuracy:.0f}%"), ("Speed", f"{wpm:.0f} WPM"),
                         ("Errors", str(app.errors)), ("Time", f"{int(elapsed)}s")):
        row = tk.Frame(content, bg=BACKGROUND)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, font=app.fonts["body"], bg=BACKGROUND, fg=PRIMARY).pack(side="left")
        tk.Label(row, text=value, font=app.fonts["body"], bg=BACKGROUND, fg=EMPHASIS).pack(side="right", padx=(40, 0))
    buttons = tk.Frame(content, bg=BACKGROUND)
    buttons.pack(fill="x", pady=(20, 0))
    close = AnimatedButton(buttons, text="Close", command=dialog.destroy)
    close.pack(side="left")
    if app.custom_text is None and app.lesson < len(LESSONS) - 1:
        def advance():
            dialog.destroy()
            app.next_lesson()

        AnimatedButton(buttons, text="Next lesson →", command=advance).pack(side="right", padx=(16, 0))
    dialog.bind("<Escape>", lambda event: (dialog.destroy(), "break")[1])
    dialog.bind("<BackSpace>", lambda event: (dialog.destroy(), "break")[1])
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.update_idletasks()
    width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
    x = max(0, app.root.winfo_rootx() + (app.root.winfo_width() - width) // 2)
    y = max(0, app.root.winfo_rooty() + (app.root.winfo_height() - height) // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.deiconify()
    dialog.grab_set()
    close.focus_set()
