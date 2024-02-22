"""
poe_exp_after_dot_tests unit_tests [<option>...] [-- <pytest_argument>...]
<option>
    --stdout
    --output=<path>
    --order
        Run test in specified default order.

Note: 'pytest' is executed from '<project_path>\\tests\\poe_exp_after_dot_tests\\unit_tests' directory. 
"""
import sys as _sys

from .              import unit_tests as _unit_tests
from .unit_tests    import _CommandArgumentError


_EXIT_SUCCESS = 0
_EXIT_FAILURE = 1


def _run(mode : str, arguments : list[str]) -> int:
    match mode:
        case "unit_tests":
            return _unit_tests._parse_and_run(arguments)
        case _:
            raise _CommandArgumentError(f"Undefined mode \"{mode}\".")


def _main(argv : list[str]) -> int:
    arguments   = argv[1:]
    mode        = arguments[0]
    arguments   = arguments[1:]
    try:
        return _run(mode, arguments)
    except _CommandArgumentError as error:
        print(error, file = _sys.stderr)
    
    return _EXIT_FAILURE