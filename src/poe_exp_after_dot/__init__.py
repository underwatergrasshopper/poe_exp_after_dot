
"""
An overlay for "Path of Exile", which displays the 2 digits after the dot from the percentage of gained experience.

Works only when "Path of Exile" is in windowed full screen.

poe_exp_after_dot.py --help
poe_exp_after_dot.py [<option> ...]
"""
__author__  = "underwatergrasshopper"
__version__ = "0.1.0"

import traceback as _traceback
import sys as _sys

from ._Private.Overlay import (
    Overlay as _Overlay
)
from ._Private.ErrorBoard import (
    run_error_board as _run_error_board,
    hide_abs_paths as _hide_abs_paths
)
from ._Private.Commons import (
    EXIT_FAILURE as _EXIT_FAILURE
)
from ._Private.LogManager import (
    to_logger as _to_logger
)


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
        _run_error_board(_hide_abs_paths(_traceback.format_exc()), str(exception))

        # All internal exceptions are handled here, if logger managed to setup correctly.
        logger = _to_logger()

        if logger and logger.hasHandlers():
            logger.critical("", exc_info = True)
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
