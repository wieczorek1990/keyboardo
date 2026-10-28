"""Settings screen presentation."""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from ..theme import BACKGROUND, EMPHASIS, FONT_BODY
from ..widgets import AnimatedButton, draw_checkbox
from ..typography import centered_padding


def build_settings(app, settings):
    root = app.root
    app.settings = tk.Frame(root, bg=BACKGROUND, padx=28, pady=12)
    AnimatedButton(app.settings, text="← Main menu", command=app.show_menu).pack(anchor="w", pady=(0, 20))
    tk.Label(app.settings, text="Settings", font=app.fonts["heading"], bg=BACKGROUND, fg=EMPHASIS).pack(anchor="w", pady=(0, 24))
    options = tk.Frame(app.settings, bg=BACKGROUND)
    options.pack(anchor="w")
    app.settings_grid = options
    app.settings_labels = []

    def label(parent, text, padx, row=None):
        widget = tk.Label(parent, text=text, font=app.fonts["body"], bg=BACKGROUND, fg=EMPHASIS)
        if row is None:
            widget.pack(side="left", padx=padx)
        else:
            widget.grid(row=row, column=0, sticky="w", padx=padx, pady=(0, 20))
        app.settings_labels.append(widget)

    label(options, "Font:", (0, 20), row=0)
    families = sorted({family for family in tkfont.families(root) if not family.startswith("@")}, key=str.casefold)
    saved_font = settings.get("font")
    app.font_choice = tk.StringVar(value=saved_font if saved_font in families else "Helvetica")
    app.font_selector = ttk.Combobox(options, textvariable=app.font_choice, values=families, state="readonly", width=26, font=app.fonts["body"], style="FontSelector.TCombobox")
    app.font_selector.grid(row=0, column=1, sticky="w", pady=(0, 20))
    app.font_selector.bind("<<ComboboxSelected>>", app.select_font)
    app.font_selector.bind("<Map>", lambda event: root.after_idle(align_settings_controls, app))
    size_row = tk.Frame(options, bg=BACKGROUND)
    size_row.grid(row=1, column=1, sticky="w", pady=(0, 20))
    label(options, "Font size:", (0, 20), row=1)
    app.font_size = tk.StringVar(value=str(settings.get("font_size", FONT_BODY[1])))
    app.size_selector = ttk.Spinbox(size_row, from_=10, to=20, textvariable=app.font_size, width=4, state="readonly", font=app.fonts["body"], style="FontSize.TSpinbox", command=app.select_font_size)
    app.size_selector.pack(side="left")
    label(size_row, "pt", (8, 0))
    label(options, "Sounds:", (0, 20), row=2)
    app.sounds_enabled = tk.BooleanVar(value=settings.get("sounds", False))
    app.checkbox_images = (tk.PhotoImage(master=root), tk.PhotoImage(master=root))
    style = ttk.Style(root)
    style.element_create("Sounds.indicator", "image", app.checkbox_images[0],
                         ("selected", app.checkbox_images[1]), sticky="")
    # Pad the lettering separately so the indicator stays centered beside it.
    style.layout("Sounds.TCheckbutton", [
        ("Sounds.indicator", {"side": "left", "sticky": ""}),
        ("Checkbutton.focus", {"side": "left", "sticky": "nswe", "children": [
            ("Checkbutton.padding", {"sticky": "nswe", "children": [
                ("Checkbutton.label", {"sticky": "nswe"})]})]})])
    app.sound_checkbox = ttk.Checkbutton(options, text="Mistakes, spaces, new lines and completion", variable=app.sounds_enabled, style="Sounds.TCheckbutton", command=app.save_settings)
    app.sound_checkbox.grid(row=2, column=1, sticky="w", pady=(0, 20))
    app.settings_message = tk.Label(app.settings, text="", font=app.fonts["small"], bg=BACKGROUND, fg=EMPHASIS)
    app.settings_message.pack(anchor="w", pady=(20, 0))

    def exit_settings(_event):
        app.show_menu()
        return "break"

    def bind_navigation(widget):
        widget.bind("<BackSpace>", exit_settings)
        widget.bind("<Escape>", app.escape_navigation)
        for child in widget.winfo_children():
            bind_navigation(child)

    bind_navigation(app.settings)


def align_settings_controls(app):
    """Center setting values, row labels, and the sound indicator optically."""
    font = app.fonts["body"]
    line_height = font.metrics("linespace")
    size = max(28, round(line_height * 1.2))
    for selected, image in enumerate(app.checkbox_images):
        draw_checkbox(image, size, selected=bool(selected))
    ttk.Style(app.root).configure("FontSize.TSpinbox", arrowsize=max(24, line_height))
    _align_entry(app.font_selector, font, "FontSelector.TCombobox")
    _align_entry(app.size_selector, font, "FontSize.TSpinbox")
    for label in app.settings_labels:
        _, top, _, bottom = centered_padding(label, font, label.cget("text"))
        if label.winfo_manager() == "grid":
            label.grid_configure(pady=(top, bottom + 20))
        else:
            label.pack_configure(pady=(top, bottom))
    _, top, _, bottom = centered_padding(app.sound_checkbox, font, app.sound_checkbox.cget("text"))
    ttk.Style(app.root).configure("Sounds.TCheckbutton", padding=(4, top, 4, bottom))


def _align_entry(selector, font, style_name):
    _, top, _, bottom = centered_padding(selector, font, selector.get())
    style = ttk.Style(selector)
    style.configure(style_name, padding=(6, top, 6, bottom))
    selector.update_idletasks()
    if not selector.winfo_ismapped():
        return
    # Combobox entry text doesn't share the field border's vertical inset.
    # Measure its real line box rather than assuming it starts inside that border.
    line_top = selector.bbox(0)[1]
    ink_center = line_top + font.metrics("linespace") / 2 - (top - bottom) / 2
    correction = round(selector.winfo_height() / 2 - ink_center)
    extra = max(0, correction - bottom, -correction - top)
    style.configure(style_name,
                    padding=(6, top + correction + extra, 6, bottom - correction + extra))
