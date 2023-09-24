
"""
An overlay for "Path of Exile", which displays the 2 digits after the dot from the percentage of gained experience.

Works only when "Path of Exile" is in windowed full screen.

poe_exp_after_dot.py [<option> ...]

<option>
    --help | -h
        Just displays this information. Application won't run.
    --data-path=<path>
        Relative or absolute path to data folder. 
        In that folder are stored: settings, logs, exp data and other data.
"""
import logging as _logging
import sys as _sys
from tkinter import messagebox as _messagebox
from ._Private.Overlay import Overlay as _Overlay, _EXIT_FAILURE


def _main(argv : list[str]) -> int:
    """
    Returns
        Exit code.

    Exceptions
        ValueError
            When any given option in argument list is incorrect
        ...
    """
    try:
        overlay = _Overlay()
        exit_code = overlay.main(argv)

    except Exception as exception:
        # All internal exceptions are handled here, if logger managed to setup correctly.
        # Wrong command line arguments are handled here only when stdout is not present (running through pyw).
        logger = _logging.getLogger("poe_exp_after_dot")

        if logger and logger.hasHandlers():
            logger.critical("", exc_info = True)
            return _EXIT_FAILURE
        elif not _sys.stdout:
            _messagebox.showerror(title = "Exception (from poe_exp_after_dot module)", message = str(exception))
            return _EXIT_FAILURE
        else:
            raise exception
    else:
        return exit_code


def main(argv : list[str] | None = None) -> int:
    """
    argv
        Command line argument list.

    Returns
        Exit code.

    Exceptions
        TypeError
        ValueError
            When any given option in argument list is incorrect
        ...
    """
    if argv is not None and not (isinstance(argv, list) and all([isinstance(option, str) for option in argv])):
        raise TypeError("Unexpected type of 'argv' parameter.")
    
    return _main(argv if argv else [])


if __name__ == "__main__":
    _sys.exit(_main(_sys.argv))
