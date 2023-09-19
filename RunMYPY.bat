:: RunMYPY.bat [<python_version>]
:: <python_version>
::     3                
::     3.11
::     3.11-32
::     3.11-64

@echo off
setlocal EnableDelayedExpansion

set PYTHON_VERSION=%1

if "!PYTHON_VERSION!" neq "" (
    set PY_PYTHON_VERSION=-!PYTHON_VERSION!
)

py -m mypy ./src ./tests_and_examples