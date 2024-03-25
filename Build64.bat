:: Build64.bat [<python_version>]
:: <python_version>
::     3                
::     3.x
::     3.11             (default)

@echo off
setlocal EnableDelayedExpansion

set PROJECT_PATH=%~dp0
set PYTHON_VERSION=%1

if "!PYTHON_VERSION!" equ "" (
    set PYTHON_VERSION=3.11
)

set PYTHON_TAG=!PYTHON_VERSION:.=!

set PY_PYTHON_VERSION=-!PYTHON_VERSION!-64

py !PY_PYTHON_VERSION! "%PROJECT_PATH%setup.py" bdist_wheel --plat-name=win-amd64 --python-tag=py!PYTHON_TAG!
