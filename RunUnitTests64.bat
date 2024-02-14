:: RunUnitTeststr.bat [<option>...] [-- <pytest_argument>...]
:: <option>
::     --stdout
::     --output=<path>          (default: '<project_path>\out\unit_tests')
:: <pytest_argument>
::     --trace
::         Invokes pdb inside pytest.
::
:: Note: 'pytest' is executed from '<project_path>\tests\poe_exp_after_dot_tests\unit_tests' directory. 

@echo off
set PROJECT_PATH=%~dp0
set PYTHONPATH=%PROJECT_PATH%src;%PYTHONPATH%
set PYTHONPATH=%PROJECT_PATH%tests;%PYTHONPATH%

py -3-64 -m poe_exp_after_dot_tests unit_tests --output="%PROJECT_PATH%out\unit_tests" %*