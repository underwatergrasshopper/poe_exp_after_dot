@echo off
set PYTHONPATH=%CD%\\src;%PYTHONPATH%
py -3-64 -m poe_exp_after_dot --data-path="./out/data" --font="Consolas,16," --overwrite-default-format %*