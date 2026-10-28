"""Reusable animated controls."""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from .theme import BACKGROUND
from .typography import centered_padding


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
