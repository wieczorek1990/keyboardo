"""Shared colors, typography, and ttk styles."""
from tkinter import ttk
from tkinter import font as tkfont

# Palette from https://soiree.tech/style.css
BACKGROUND = "#a6dbff"
SURFACE = "#dbf1ff"
EMPHASIS = "#586e75"
PRIMARY = "#657b83"
ACCENT = "#859900"

FONT_BRAND = ("Helvetica", 26, "bold")
FONT_HEADING = ("Helvetica", 22, "bold")
FONT_BODY = ("Helvetica", 14)
FONT_SMALL = ("Helvetica", 12)
FONT_SELECTOR = ("Helvetica", 18)
FONT_ARROW = ("Helvetica", 22)
FONT_TYPING = ("Menlo", 22)


def configure_theme(root):
    fonts = {
        "brand": tkfont.Font(root=root, font=FONT_BRAND),
        "heading": tkfont.Font(root=root, font=FONT_HEADING),
        "body": tkfont.Font(root=root, font=FONT_BODY),
        "small": tkfont.Font(root=root, font=FONT_SMALL),
        "selector": tkfont.Font(root=root, font=FONT_SELECTOR),
        "arrow": tkfont.Font(root=root, font=FONT_ARROW),
        "typing": tkfont.Font(root=root, font=FONT_TYPING),
    }
    base_font_sizes = {role: font.cget("size") for role, font in fonts.items()}
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TButton", font=fonts["body"], anchor="center", padding=(12, 7), background=SURFACE, foreground=EMPHASIS)
    style.configure("LessonArrow.TButton", font=fonts["arrow"], padding=(8, 2))
    style.map("TButton", background=[("active", BACKGROUND)], foreground=[("disabled", PRIMARY)])
    style.configure("TEntry", fieldbackground=SURFACE, foreground=EMPHASIS, insertcolor=EMPHASIS)
    style.configure("TCheckbutton", font=fonts["body"], background=BACKGROUND, foreground=EMPHASIS)
    style.map("TCheckbutton", background=[("active", BACKGROUND)])
    return fonts, base_font_sizes
