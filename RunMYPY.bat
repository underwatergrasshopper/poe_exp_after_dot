:: RunMYPY.bat [<python_version>]
:: <python_version>
::     3                
::     3.11
::     3.11-32
::     3.11-64      (default)
::     3-64         

@echo off
setlocal EnableDelayedExpansion

set PROJECT_PATH=%~dp0
set PYTHON_VERSION=%1

if "!PYTHON_VERSION!" neq "" (
    set PY_PYTHON_VERSION=-!PYTHON_VERSION!
) else (
    set PY_PYTHON_VERSION=-3.11-64
)

py !PY_PYTHON_VERSION! -m mypy "%PROJECT_PATH%src" "%PROJECT_PATH%tests"