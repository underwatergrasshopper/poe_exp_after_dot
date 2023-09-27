:: RunMYPY.bat [<python_version>]
:: <python_version>
::     3                
::     3.11
::     3.11-32
::     3.11-64
::     3-64         (default)

@echo off
setlocal EnableDelayedExpansion

set PYTHON_VERSION=%1

if "!PYTHON_VERSION!" neq "" (
    set PY_PYTHON_VERSION=-!PYTHON_VERSION!
) else (
    set PY_PYTHON_VERSION=-3-64
)

py !PY_PYTHON_VERSION! -m mypy ./src ./tests