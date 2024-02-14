@echo off
set PROJECT_PATH=%~dp0
set PYTHONPATH=%PROJECT_PATH%src;%PYTHONPATH%

py -3-64 -m poe_exp_after_dot --data-path="%PROJECT_PATH%out\data" --font="Consolas,16," --overwrite-default-format %*
echo "%PROJECT_PATH%out\data"