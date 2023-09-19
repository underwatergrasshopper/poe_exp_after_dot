import pytest as _pytest
import os as _os

def run(
        targets             : list[str] | None  = None, 
        output_path         : str | None        = None, 
        is_stdout_enabled   : bool              = False
            ):
    """
    targets
        List of test script file names. They can be extended with test function name. 
        Similarly to how pytest is doing this: '<test_script_name>[::<test_function_name>]'.
        Examples:
            test_area.py
            test_area.py::test_area
    """
    if targets is not None and not (isinstance(targets, list) and all(isinstance(item, str) for item in targets)):
        raise TypeError("Unexpected type of 'targets' parameter.")
    
    if output_path is not None and not isinstance(output_path, str):
        raise TypeError("Unexpected type of 'output_path' parameter.")
    
    if not isinstance(is_stdout_enabled, bool):
        raise TypeError("Unexpected type of 'is_stdout_enabled' parameter.")
    
    _run(targets, output_path, is_stdout_enabled)


def _run(
        targets             : list[str] | None,
        output_path         : str | None, 
        is_stdout_enabled   : bool
            ):
    base_path = _os.path.relpath(_os.path.dirname(__file__)) + "/"

    if targets:
        targets = [base_path + target for target in targets]
    else:
        targets = [base_path]

    options = "--no-header -v -x".split(" ")
    if is_stdout_enabled:   options += ["-s"]
    if output_path:         options += ["--basetemp=" + output_path]

    _pytest.main(targets + options)
