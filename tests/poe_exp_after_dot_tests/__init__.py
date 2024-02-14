"""
poe_exp_after_dot_tests unit_tests [<option>...] [-- <pytest_argument>...]
<option>
    --stdout
    --output=<path>

Note: 'pytest' is executed from '<project_path>\\tests\\poe_exp_after_dot_tests\\unit_tests' directory. 
"""
from . import unit_tests as _unit_tests


_EXIT_SUCCESS = 0
_EXIT_FAILURE = 1


def _main(argv : list[str]) -> int:
    arguments = argv[1:]
    mode = arguments[0]
    match mode:
        case "unit_tests":
            return _unit_tests._parse_and_run(arguments[1:])
        case undefined:
            raise ValueError(f"Undefined mode \"{undefined}\".")
    
    return _EXIT_FAILURE


def main(argv : list[str] | None = None) -> int:
    if argv is not None and not (isinstance(argv, list) and all(isinstance(item, str) for item in argv)):
       raise TypeError("Unexpected type of 'argv' parameter.")
    
    return _main(argv if argv is not None else [])