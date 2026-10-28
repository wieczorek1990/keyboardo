"""Reusable animated controls."""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from .theme import ACCENT, BACKGROUND, EMPHASIS, SURFACE
from .typography import centered_padding


def draw_checkbox(image, size, selected=False):
    """Draw a scalable checkbox without relying on the theme's fixed-size mark."""
    image.configure(width=size, height=size)
    image.blank()
    image.put(EMPHASIS, to=(2, 2, size - 2, size - 2))
    image.put(SURFACE, to=(4, 4, size - 4, size - 4))
    if not selected:
        return
    points = ((0.23, 0.51), (0.43, 0.72), (0.78, 0.28))
    radius = max(1.5, size * 0.055)
    for start, end in zip(points, points[1:]):
        ax, ay = start[0] * size, start[1] * size
        dx, dy = (end[0] - start[0]) * size, (end[1] - start[1]) * size
        for y in range(4, size - 4):
            for x in range(4, size - 4):
                t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
                if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= radius ** 2:
                    image.put(ACCENT, to=(x, y, x + 1, y + 1))


class AnimatedButton(ttk.Button):
    """Center visible lettering and animate within a fixed layout slot."""

    def __init__(self, parent, font=None, **kwargs):
        self.slot = tk.Frame(parent, bg=BACKGROUND)
        self.styles = ttk.Style(parent)
        base_style = kwargs.pop("style", "TButton")
        if font is None:
            font_spec = self.styles.lookup(base_style, "font") or "TkDefaultFont"
            try:
                font = tkfont.nametofont(str(font_spec), root=parent)
            except tk.TclError:
                font = tkfont.Font(root=parent, font=font_spec)
        self.label_font = font
        self.label_style = f"Button{id(self)}.{base_style}"
        self.styles.configure(self.label_style, font=font, anchor="center")
        self.action = kwargs.pop("command", None)
        self.animation = None
        self.animating = False
        super().__init__(self.slot, style=self.label_style, command=self.animate, **kwargs)
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self.refresh_size()
        self.bind("<Destroy>", self.cancel_animation, add="+")

    def pack(self, **kwargs):
        self.refresh_size()
        self.slot.pack(**kwargs)

    def refresh_size(self):
        padding = centered_padding(self, self.label_font, self.cget("text"))
        self.styles.configure(self.label_style, padding=padding)
        # ttk recalculates font and padding requests on the next idle pass.
        self.update_idletasks()
        self.slot.configure(width=self.winfo_reqwidth(), height=self.winfo_reqheight())

    def animate(self):
        if self.animating or self.instate(["disabled"]):
            return
        self.animating = True
        self.animate_step(0)

    def animate_step(self, index):
        scales = (0.97, 0.93, 0.90, 0.93, 0.97, 1.0)
        self.animation = None
        if index < len(scales):
            self.place_configure(relwidth=scales[index], relheight=scales[index])
            self.animation = self.after(20, self.animate_step, index + 1)
        else:
            self.animating = False
            if not self.instate(["disabled"]) and self.action:
                self.action()

    def cancel_animation(self, _event):
        if self.animation is not None:
            self.after_cancel(self.animation)
            self.animation = None
