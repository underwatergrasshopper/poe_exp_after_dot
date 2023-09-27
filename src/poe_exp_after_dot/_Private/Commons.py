from typing import Any
import typing
from PySide6.QtWidgets import QApplication

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