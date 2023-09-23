
import logging as _logging
from ._Private.Overlay import Overlay as _Overlay

def _main(argv : list[str]) -> int:
    overlay = _Overlay()
    return overlay.main(argv)

def _main_try_log_when_exception(argv : list[str]) -> int:
    try:
        exit_code = _main(argv)
    except Exception as exception:
        logger = _logging.getLogger("poe_exp_after_dot")
        if logger and logger.hasHandlers():
            logger.critical("", exc_info = True)
            return 1
        else:
            raise exception
    else:
        return exit_code

if __name__ == "__main__":
    import sys as _sys

    _sys.exit(_main_try_log_when_exception(_sys.argv))