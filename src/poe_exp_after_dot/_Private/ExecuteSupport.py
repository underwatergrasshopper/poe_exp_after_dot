import os       as _os
import winreg   as _winreg


_RUN_FILE_CONTENT = """
@echo off

start pyw -3-64 -m poe_exp_after_dot
""".strip("\n")


def _get_register_value(name : str, path : str):
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, path, 0, _winreg.KEY_READ)
    value, type_ = _winreg.QueryValueEx(key, name)
    _winreg.CloseKey(key)
    return value


def make_run_file():
    desktop_path = _get_register_value("Desktop", "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
    desktop_path = _os.path.expandvars(desktop_path)
    run_file_name = desktop_path + "/poe_exp_after_dot.bat"

    with open(run_file_name, "w") as file:
        file.write(_RUN_FILE_CONTENT)