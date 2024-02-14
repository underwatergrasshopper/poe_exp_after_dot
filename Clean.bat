@echo off
set PROJECT_PATH=%~dp0

if exist "%PROJECT_PATH%dist" rd /s /q "%PROJECT_PATH%dist"
if exist "%PROJECT_PATH%build" rd /s /q "%PROJECT_PATH%build"
if exist "%PROJECT_PATH%out" rd /s /q "%PROJECT_PATH%out"
if exist "%PROJECT_PATH%log" rd /s /q "%PROJECT_PATH%log"
if exist "%PROJECT_PATH%src\poe_exp_after_dot.egg-info" rd /s /q "%PROJECT_PATH%src\poe_exp_after_dot.egg-info"

echo done