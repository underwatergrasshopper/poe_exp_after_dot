import pytest   as _pytest
import os       as _os


class _CommandArgumentError(Exception):
    pass


def _parse_and_run(arguments : list[str]) -> int:
    try:
        index = arguments.index("--")
    except ValueError:
        pytest_arguments = []
    else:
        pytest_arguments = arguments[index + 1:]
        arguments = arguments[:index]

    output_path         : str | None    = None
    is_stdout_enabled   : bool          = False

    for argument in arguments:
        name, *value = argument.split("=", 1)
        match (name, *value):
            case ["--output", output_path]:
                output_path = _os.path.abspath(output_path)
            case ["--stdout"]:
                is_stdout_enabled = True
            case ["--order"]:
                pytest_arguments = _order + pytest_arguments

            case ["--output" | "--order"]:
                raise _CommandArgumentError(f"Option \"{name}\" need to have value.")
            case ["--stdout", _]:
                raise _CommandArgumentError(f"Option \"{name}\" can not have value.")
            case [name, *_]:
                raise _CommandArgumentError(f"Option \"{name}\" is unknown.")
            
    return _run(output_path, is_stdout_enabled, pytest_arguments)


def _run(
        output_path         : str | None, 
        is_stdout_enabled   : bool,
        pytest_arguments    : list[str],
            ) -> int:
    base_path = _os.path.abspath(_os.path.dirname(__file__))
    print(f"Warning!!! 'pytest' is running from '{base_path}' directory.")

    options = "--no-header -v -x".split(" ")
    if is_stdout_enabled:   options += ["-s"]
    if output_path:         options += ["--basetemp=" + output_path]

    _os.makedirs(output_path, exist_ok = True)

    run_path = _os.getcwd()
    _os.chdir(base_path)

    try:
        exit_code = _pytest.main(options + pytest_arguments)
    finally:
        _os.chdir(run_path)

    return exit_code


_order = [
    "test_commons.py",
    "test_fine_formatters.py",

    "test_template_loader.py",
    "test_text_generator.py",

    "test_settings.py",
    "test_measurer.py",
    "test_logic.py",
    "test_overlay.py",
]


