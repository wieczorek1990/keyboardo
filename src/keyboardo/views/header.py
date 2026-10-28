"""Header screen presentation."""
import tkinter as tk

from ..theme import BACKGROUND, EMPHASIS, PRIMARY
from ..resources import resource_path


def build_header(app):
    root = app.root
    header = tk.Frame(root, bg=BACKGROUND, padx=28, pady=22)
    app.header = header
    header.pack(fill="x")
    app.logo = tk.PhotoImage(file=str(resource_path("logo-header.png")))
    root.iconphoto(True, app.logo)
    tk.Label(header, image=app.logo, bg=BACKGROUND).pack(side="left", padx=(0, 16))
    brand = tk.Frame(header, bg=BACKGROUND)
    brand.pack(side="left")
    tk.Label(brand, text="Keyboardo", font=app.fonts["brand"], bg=BACKGROUND, fg=EMPHASIS).pack(anchor="w")
    tk.Label(brand, text="A little practice. A lighter touch.", font=app.fonts["small"], bg=BACKGROUND, fg=PRIMARY).pack(anchor="w")
