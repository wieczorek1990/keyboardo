"""Measure visible glyphs for optically centered macOS button labels."""
import ctypes
from ctypes.util import find_library
from functools import lru_cache
import sys


class _Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


class _Size(ctypes.Structure):
    _fields_ = [("width", ctypes.c_double), ("height", ctypes.c_double)]


class _Rect(ctypes.Structure):
    _fields_ = [("origin", _Point), ("size", _Size)]


@lru_cache(maxsize=1)
def _core_text():
    cf = ctypes.CDLL(find_library("CoreFoundation"))
    ct = ctypes.CDLL(find_library("CoreText"))
    pointer = ctypes.c_void_p
    cf.CFStringCreateWithCString.argtypes = [pointer, ctypes.c_char_p, ctypes.c_uint32]
    cf.CFStringCreateWithCString.restype = pointer
    cf.CFDictionaryCreate.argtypes = [pointer, ctypes.POINTER(pointer), ctypes.POINTER(pointer), ctypes.c_long, pointer, pointer]
    cf.CFDictionaryCreate.restype = pointer
    cf.CFAttributedStringCreate.argtypes = [pointer, pointer, pointer]
    cf.CFAttributedStringCreate.restype = pointer
    cf.CFRelease.argtypes = [pointer]
    ct.CTFontCreateWithName.argtypes = [pointer, ctypes.c_double, pointer]
    ct.CTFontCreateWithName.restype = pointer
    ct.CTLineCreateWithAttributedString.argtypes = [pointer]
    ct.CTLineCreateWithAttributedString.restype = pointer
    ct.CTLineGetBoundsWithOptions.argtypes = [pointer, ctypes.c_ulong]
    ct.CTLineGetBoundsWithOptions.restype = _Rect
    return cf, ct


@lru_cache(maxsize=256)
def _glyph_bounds(family, pixels, text):
    cf, ct = _core_text()
    pointer = ctypes.c_void_p
    objects = []

    def keep(value):
        if not value:
            raise ValueError("Could not measure font glyphs")
        objects.append(value)
        return value

    def string(value):
        return keep(cf.CFStringCreateWithCString(None, value.encode("utf-8"), 0x08000100))

    try:
        name = string(family)
        font = keep(ct.CTFontCreateWithName(name, pixels, None))
        label = string(text)
        key = pointer.in_dll(ct, "kCTFontAttributeName")
        attributes = keep(cf.CFDictionaryCreate(None, (pointer * 1)(key.value),
                                               (pointer * 1)(font), 1, None, None))
        attributed = keep(cf.CFAttributedStringCreate(None, label, attributes))
        line = keep(ct.CTLineCreateWithAttributedString(attributed))
        # kCTLineBoundsUseGlyphPathBounds excludes invisible ascent/descent space.
        bounds = ct.CTLineGetBoundsWithOptions(line, 1 << 3)
        return bounds.origin.x, bounds.origin.y, bounds.size.width, bounds.size.height
    finally:
        for value in reversed(objects):
            cf.CFRelease(value)


def centered_padding(widget, font, text):
    """Balance padding around visible letters instead of the font's line box."""
    x_offset = y_offset = 0
    if sys.platform == "darwin" and text:
        size = font.cget("size")
        pixels = size * float(widget.tk.call("tk", "scaling")) if size > 0 else -size
        try:
            x, y, width, height = _glyph_bounds(font.actual("family"), pixels, text)
            x_offset = round((font.measure(text) - width) / 2 - x)
            y_offset = round(font.metrics("linespace") / 2 - font.metrics("ascent") + y + height / 2)
        except (OSError, AttributeError, ValueError):
            pass
    horizontal = max(12, abs(x_offset) + 2)
    vertical = max(7, abs(y_offset) + 2)
    return horizontal + x_offset, vertical + y_offset, horizontal - x_offset, vertical - y_offset
