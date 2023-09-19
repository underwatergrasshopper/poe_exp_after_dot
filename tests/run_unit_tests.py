"""
run_unit_tests.py [--stdout] [<test_script_name>[::<test_function_name>] ...]
    --stdout        - Displays prints to stdout.

Note: Similarly to how pytest is doing this.

Examples:
    run_unit_tests.py test_area.py
    run_unit_tests.py test_area.py test_basics.py
    run_unit_tests.py test_area.py::test_area
"""

if __name__ == "__main__":
    import _setup_path_env
    _setup_path_env.run()
   
import os as _os
import re as _re
import poe_exp_after_dot_tests.unit_tests as _unit_tests

def main(argv : list[str] | None = None):
    """
    argv
       List of test script file names. They can be extended with test function name. 
       Similarly to how pytest is doing this: '<test_script_name>[::<test_function_name>]'.
       Examples:
          test_area.py
          test_area.py::test_area
    """
    if argv is not None and not (isinstance(argv, list) and all(isinstance(item, str) for item in argv)):
       raise TypeError("Unexpected type of 'argv' parameter.")
    
    _main(argv if argv else [])

def run(targets : list[str] | None = None, is_stdout_enabled : bool = False):
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
    
    if not isinstance(is_stdout_enabled, bool):
       raise TypeError("Unexpected type of 'is_stdout_enabled' parameter.")
    
    _run(targets, is_stdout_enabled)

def _main(argv : list[str]):
    args = argv[1:]

    is_stdout_enabled = "--stdout" in args

    def is_not_option(arg):
        return _re.match(r"-.*", arg) is None

    targets = list(filter(is_not_option, args))

    _run(targets, is_stdout_enabled)

def _run(targets : list[str] | None, is_stdout_enabled : bool = False):
    output_rel_path = _os.path.relpath(_os.path.dirname(__file__) + "/../out/unit_tests")
    _unit_tests._run(targets, output_rel_path, is_stdout_enabled)

if __name__ == "__main__":
    import sys as _sys 
 
    _main(_sys.argv)