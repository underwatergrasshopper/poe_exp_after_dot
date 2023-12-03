# Description

An overlay for the "Path of Exile" game. Displays additional experience bar, which represent experience progress in fractional part of percent (two digits after dot). 

In addition to that, displays other statistics.
Displays average experience gain since last measure, both in exp/h and in percent. 
Displays time needed to gain next level and time needed to gain next 10% of experience. 

# How it works

Requires the "Path of Exile" window to be in "Windowed Fullscreen" mode.

This program takes a screenshot of the "Path of Exile" window and scans the part of the screenshot, where the in game exp tooltip is, to fetch current exp value. It's considered as a measure. Calculates experience gain between last and current measure.

This program brings "Path of Exile" window back to foreground every time any overlay element is clicked.

It also checks if "Path of Exile" window is on foreground. Then hides overlay if it isn't on foreground, and shows overlay if it is on foreground.

This program doesn't modify any Path of Exile files.
This program doesn't read any character data from GGG server.

Interactions:
```
Measure - LMB on in game exp bar.
Help    - Hold Shift + RMB on in game exp bar.
```

# Requirements

|||
|---|---| 
| System | Windows 10 |
| Python | 3.11 64bit (or above) |
| py launcher | Yes |

# How to install

## From `PyPi` database (recommended)

Run `py 3-64 -m pip install poe_exp_after_dot` in console window.

## From `.whl` file

Go to `Releases` in github side panel. Download `poe_exp_after_dot-<version>-py3-none-win_amd64.whl` from latest release.
Run `py 3-64 -m pip install poe_exp_after_dot-<version>-py3-none-win_amd64.whl` in console window.

# How to uninstall

Run `py 3-64 -m pip uninstall poe_exp_after_dot` in console window.

# How to run

Run `poe_exp_after_dot.bat` from desktop.

... or ...

Run `start pyw 3-64 -m poe_exp_after_dot` in console window.




