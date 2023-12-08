:: RunUnitTeststr.bat [<option>...] [-- <pytest_argument>...]
:: <option>
::     --stdout
::     --output=<path>          (default: './out/unit_tests')
::
:: Note: 'pytest' is executed from '<project_path>/tests/poe_exp_after_dot_tests/unit_tests' directory. 

@echo off
set PYTHONPATH=%CD%\\src;%PYTHONPATH%
set PYTHONPATH=%CD%\\tests;%PYTHONPATH%
py -3-64 -m poe_exp_after_dot_tests unit_tests --output=./out/unit_tests %*