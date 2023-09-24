
import logging as _logging
from ._Private.Overlay import Overlay as _Overlay, _EXIT_FAILURE


def _main(argv : list[str]) -> int:
    """
    Returns
        Exit code.
    """
    try:
        overlay = _Overlay()
        exit_code = overlay.main(argv)

    except Exception as exception:
        # All internal exceptions are handled here, if logger managed to setup correctly.
        logger = _logging.getLogger("poe_exp_after_dot")

        if logger and logger.hasHandlers():
            logger.critical("", exc_info = True)
            return _EXIT_FAILURE
        else:
            raise exception
    else:
        return exit_code


def main(argv : list[str] | None = None) -> int:
    """
    Returns
        Exit code.
    """
    if argv is not None and not (isinstance(argv, list) and all([isinstance(option, str) for option in argv])):
        raise TypeError("Unexpected type of 'argv' parameter.")
    
    return _main(argv if argv else [])


if __name__ == "__main__":
    import sys as _sys

    _sys.exit(_main(_sys.argv))