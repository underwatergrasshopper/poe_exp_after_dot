@echo off

if exist "./dist" rd /s /q "./dist"
if exist "./build" rd /s /q "./build"
if exist "./out" rd /s /q "./out"
if exist "./log" rd /s /q "./log"
if exist "./src/poe_exp_after_dot.egg-info" rd /s /q "./src/poe_exp_after_dot.egg-info"

echo done