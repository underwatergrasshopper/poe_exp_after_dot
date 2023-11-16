from typing import Any
import typing
from PySide6.QtWidgets import QApplication

import re as _re

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def pad_to_length(text : str, length : int):
    """
    If 'text' is shorter than 'length', then adds padding to front of 'text', until length of text is equal to 'length'.
    If 'text' is longer than 'length', then shorts 'text', until length of text is equal to 'length'.
    """
    return text.rjust(length)[:length]

def to_app() -> QApplication:
    app = QApplication.instance()
    if app:
        return typing.cast(QApplication, app)
    return QApplication([])

def merge_on_all_levels(a : dict, b : dict) -> dict:
    """
    Merges 'b' into 'a' on all levels.
    """
    c = {}
    c.update(a)
    for k, v in b.items():
        if isinstance(v, dict) and k in c and isinstance(c[k], dict):
            c[k] = merge_on_all_levels(c[k], v)
        else:
            c[k] = v
    return c

def time_unit_to_short(time_unit : str) -> str:
    return _short_time_units[time_unit]

_short_time_units = {
    "second"    : "s",
    "minute"    : "m",
    "hour"      : "h",
    "day"       : "d",
    "week"      : "w",
}

def hide_abs_paths(traceback_message : str) -> str:
    lines = traceback_message.split("\n")
    formatted_lines = []
    for line in lines:
        formatted_lines.append(_re.sub(r"File \".*([\\/]poe_exp_after_dot.*\.py)\"|File \".*([\\/][^\\/]+\.py)\"", "File \"...\\1\"", line))
    return ("\n".join(formatted_lines)).strip("\n")

def apply_qt_escape_sequences(text : str) -> str:
    html_escape_map = [
        ("<", "&lt;"), 
        (">", "&gt;"),
        ("&", "&amp;"),
    ]
    for escape in html_escape_map:
        text = text.replace(escape[0], escape[1])
    return text
