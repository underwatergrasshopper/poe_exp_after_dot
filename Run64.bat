@echo off
set PATH=src;%PATH%
py -3-64 .\\tests\\run.py --data-path="./out/data" --font="Consolas,14,bold" %*