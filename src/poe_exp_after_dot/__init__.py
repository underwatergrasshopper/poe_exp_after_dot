
"""
An overlay for "Path of Exile", which displays the 2 digits after the dot from the percentage of gained experience.

Works only when "Path of Exile" is in windowed full screen.

poe_exp_after_dot.py --help
poe_exp_after_dot.py [<option>...]
"""
__author__  = "underwatergrasshopper"
__version__ = "0.1.5r2"


import os           as _os
import sys          as _sys
import traceback    as _traceback

from ._Private.Overlay      import Overlay as _Overlay
from ._Private.LogManager   import to_logger as _to_logger
from ._Private.Commons      import (
    EXIT_FAILURE            as _EXIT_FAILURE,
    hide_abs_paths          as _hide_abs_paths,
    run_error_board         as _run_error_board,
    get_argument_value      as _get_argument_value,
    get_default_data_path   as _get_default_data_path
)
from ._Private.Version      import set_version as _set_version

from .Exceptions import (
    Error, 
    CommandArgumentError, 
    TemplateLoadFail, 
    TextGenFail
)


def _main(argv : list[str], *, is_pass_all_exceptions_through : bool = False) -> int:
    """
    Returns
        Exit code.

    Exceptions
        ValueError
            When any given option in argument list is incorrect
        ...
    """
    _set_version(__version__)
    try:
        overlay = _Overlay()
        exit_code = overlay.main(argv)
    except CommandArgumentError as error:
        if is_pass_all_exceptions_through:
            raise
        print(str(error))
        return _EXIT_FAILURE
    except Exception as exception:
        # Displays exception message in ErrorBoard.
        
        # Workaround!!!
        # When inside except, some pyqt widgets from overlay still exists. 
        # To prevent displaying them with error board, os.system is used for running error board in separate window.

        data_path = _get_argument_value("--data-path", argv[1:])
        if data_path is None:
            data_path = _get_default_data_path()
        else:
            data_path = data_path.lstrip("/").lstrip("\\").lstrip("\\")

        if isinstance(exception, Error):
            short_message = str(exception)
        else:
            short_message = "Inner error. Check 'runtime.log' in Data Folder."

        error_board_launch_error_code = _run_error_board(
            data_path,
            _hide_abs_paths(_traceback.format_exc()),
            short_message
        )

        # All internal exceptions are handled here, if logger managed to setup correctly.
        logger = _to_logger()

        if logger and logger.hasHandlers():
            logger.critical("", exc_info = True)

            if error_board_launch_error_code != 0:
                logger.error(f"ErrorBoard failed to launch, error code: {error_board_launch_error_code}.")

            return _EXIT_FAILURE
        else:
            raise
    else:
        return exit_code


def main(argv : list[str] | None = None, *, is_pass_all_exceptions_through : bool = False) -> int:
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
    if not isinstance(is_pass_all_exceptions_through, bool):
        raise TypeError("Unexpected type of 'is_pass_all_exceptions_through' parameter.")
    
    return _main(argv if argv else [], is_pass_all_exceptions_through = is_pass_all_exceptions_through)
