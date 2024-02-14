@echo off
set PROJECT_PATH=%~dp0
set PYTHONPATH=%PROJECT_PATH%src;%PYTHONPATH%

py -3-64 -m poe_exp_after_dot --data-path="./out/data" --font="Consolas,16," --overwrite-default-format %*