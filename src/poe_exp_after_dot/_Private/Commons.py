import re       as _re
import os       as _os
import typing   as _typing

from typing import Any

from PySide6.QtWidgets import QApplication


# path to top level package
_base_path = _os.path.abspath(_os.path.dirname(__file__) + "\\..")


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
        return _typing.cast(QApplication, app)
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


def get_argument_value(name, arguments : list[str]) -> str | None:
    for argument in arguments:
        argument_name, *value = argument.split("=", 1)
        if argument_name == name:
            return value[0] if value else None
    return None


def get_default_data_path() -> str:
    return _os.path.abspath(_os.environ["APPDATA"] + "\\..\\Local\\poe_exp_after_dot")


def run_error_board(data_path : str, message : str, short_message : str, *, is_details : bool = False) -> int:
    """
    Runs ErrorBoard and does not wait.

    Returns
        Error code.
    """
    message = apply_qt_escape_sequences(message).replace("\n", "<br>")
    short_message = apply_qt_escape_sequences(short_message).replace("\n", "<br>")

    cache_path = data_path + "\\cache"
    _os.makedirs(cache_path, exist_ok=True)

    error_board_file_name = _base_path + "\\_Private\\GUI\\ErrorBoard.py"

    message_file_name = cache_path + "\\last_exception_message_preprocessed.txt"    
    short_message_file_name = cache_path + "\\last_exception_short_message_preprocessed.txt"

    with open(message_file_name, "w") as file:
        file.write(message)

    with open(short_message_file_name, "w") as file:
        file.write(short_message)

    is_pyw = _os.system("where /Q pyw") == 0
    launcher = "pyw -3.11-64" if is_pyw else "pythonw"

    options = []
    if is_details:
        options.append("--details")
    options = " ".join(options)

    return _os.system(f"start {launcher} \"{error_board_file_name}\" \"{data_path}\" \"{message_file_name}\" \"{short_message_file_name}\" {options}")


def character_name_to_log_name(character_name : str):
    if character_name:
        return f"\"{character_name}\""
    else:
        return "Generic Character"
