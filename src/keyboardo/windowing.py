"""Center the complete window inside the desktop's usable area on macOS."""
import ctypes
from ctypes.util import find_library
from functools import lru_cache
import platform
import sys


class _Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


class _Size(ctypes.Structure):
    _fields_ = [("width", ctypes.c_double), ("height", ctypes.c_double)]


class _Rect(ctypes.Structure):
    _fields_ = [("origin", _Point), ("size", _Size)]


@lru_cache(maxsize=1)
def _runtime():
    ctypes.CDLL(find_library("AppKit"))
    objc = ctypes.CDLL(find_library("objc"))
    objc.objc_getClass.argtypes = [ctypes.c_char_p]
    objc.objc_getClass.restype = ctypes.c_void_p
    objc.sel_registerName.argtypes = [ctypes.c_char_p]
    objc.sel_registerName.restype = ctypes.c_void_p
    return objc


def _send(receiver, selector, result=ctypes.c_void_p, arguments=(), values=()):
    objc = _runtime()
    signature = ctypes.CFUNCTYPE(result, ctypes.c_void_p, ctypes.c_void_p, *arguments)
    method = signature(("objc_msgSend", objc))
    return method(receiver, objc.sel_registerName(selector.encode()), *values)


def _rect(receiver, selector):
    if platform.machine() == "x86_64":
        # Intel's ABI returns a 32-byte NSRect through a separate result pointer.
        objc = _runtime()
        result = _Rect()
        signature = ctypes.CFUNCTYPE(None, ctypes.POINTER(_Rect), ctypes.c_void_p, ctypes.c_void_p)
        signature(("objc_msgSend_stret", objc))(ctypes.byref(result), receiver,
                                              objc.sel_registerName(selector.encode()))
        return result
    return _send(receiver, selector, _Rect)


def _native_window(window):
    application = _send(_runtime().objc_getClass(b"NSApplication"), "sharedApplication")
    windows = _send(application, "windows")
    for index in range(_send(windows, "count", ctypes.c_ulong)):
        native = _send(windows, "objectAtIndex:", arguments=(ctypes.c_ulong,), values=(index,))
        title = _send(_send(native, "title"), "UTF8String", ctypes.c_char_p)
        if title and title.decode("utf-8") == window.title():
            return native
    return None


def center_on_desktop(window):
    """Use the current screen's visible frame, including title-bar dimensions."""
    window.update_idletasks()
    if sys.platform == "darwin":
        try:
            native = _native_window(window)
            screen = _send(native, "screen") if native else None
            if screen:
                desktop = _rect(screen, "visibleFrame")
                frame = _rect(native, "frame")
                origin = _Point(desktop.origin.x + (desktop.size.width - frame.size.width) / 2,
                                desktop.origin.y + (desktop.size.height - frame.size.height) / 2)
                _send(native, "setFrameOrigin:", None, (_Point,), (origin,))
                return
        except (OSError, AttributeError, ValueError):
            pass
    x = max(0, (window.winfo_screenwidth() - window.winfo_width()) // 2)
    y = max(0, (window.winfo_screenheight() - window.winfo_height()) // 2)
    window.geometry(f"+{x}+{y}")
