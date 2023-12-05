# Description

An overlay for the "Path of Exile" game. Displays additional experience bar, which represent experience progress in fractional part of percent (two digits after dot). 

In addition to that, displays other statistics.
Displays average experience gain since last measure, both in exp/h and in percent. 
Displays time needed to gain next level and time needed to gain next 10% of experience. 

# How it works

Requires the "Path of Exile" window to be in "Windowed Fullscreen" mode.

This program takes a screenshot of the "Path of Exile" window and scans the part of the screenshot, where the in game exp tooltip is, to fetch current exp value. It's considered as a measure. Calculates an experience gain between last and current measure.

This program brings "Path of Exile" window back to foreground every time any overlay element is clicked.

It also checks if "Path of Exile" window is on foreground. Then hides overlay if it isn't on foreground, and shows overlay if it is on foreground.

This program doesn't modify any "Path of Exile" files.
This program doesn't read any character data from GGG server.

# Requirements

|||
|---|---| 
| System | Windows 10 |
| Python | 3.11 64bit (or above) |
| py launcher | Yes |

# How to install

## From `PyPi` database (recommended)

Run `py -3-64 -m pip install poe_exp_after_dot` in console window.

## From `.whl` file

Go to `Releases` in github side panel. Download `poe_exp_after_dot-<version>-py3-none-win_amd64.whl` from latest release.
Run `py -3-64 -m pip install poe_exp_after_dot-<version>-py3-none-win_amd64.whl` in console window.

# How to uninstall

Run `py -3-64 -m pip uninstall poe_exp_after_dot` in console window.

# How to run

Run `poe_exp_after_dot.bat` from desktop.

... or ...

Run `start pyw -3-64 -m poe_exp_after_dot` in console window.

# Command Line

Run `py -3-64 -m poe_exp_after_dot --help` to see available options.

# Controls and Navigation

Actions which can be performed on In-Game Experience Bar area (also known as ControlRegion):

```
LMB                         - Measure (removes following entries nad creates new entry)
Ctrl + LMB                  - Next Entry
Ctrl + Shift + LMB          - Last Entry
Ctrl + RMB                  - Previous Entry
Ctrl + Shift + RMB          - Before First Entry
Hold MMB                    - Show Entry with Page and Date
Scroll Wheel                - Next/Previous Entry
Ctrl + Shift + Alt + LMB    - Remove current Entry with all following Entries
RMB                         - Menu
Hover                       - Show InfoBoard
Hold Shift + RMB            - Show Help
```

Each successful Measure is stored as an Entry. 

Unsuccessful Measures are not stored. They can be recognized by having `ERR` in InfoBoard at very beginning.

*Note: Why unsuccessful measures appear? Current experience value is scanned by AI from in-game experience toolbar. Sometimes scan might not recognize text correctly or be incomplete. Usually when the toolbar does not appear at all.*

Menu can be accessed from tray icon bar. There should be icon `poe dot exp`. Right Click on that icon opens menu.

Glossary:
* `LMB` - Left Mouse Button
* `RMB` - Right Mouse Button
* `MMB` - Middle Mouse Button

# GUI Layout

![GUI Layout](./docs/images/GUI_Layout.png)

# Hierarchy of Data Folder

```
<data_folder_name>
    settings.json
    exp_data.json
    runtime.log
    cache/
    formats/
        Default.format
        *.format
    characters/
        <character_name>
            exp_data.json
```

`<data_folder_name>` by default is `poe_exp_after_dot`.

Data folder is located by default in `%APPDATA%/../Local`.

`Default.format` is file where format of InfoBoard text is stored.

`exp_data.json` if file where measure entries are stored.

`character/` if folder where measure entries are stored for specific characters.

# How to run tests

All following actions are taken from project folder.

Run `py -3-64 -m pip install -r tests_and_examples_requirements.txt` in command window to install test dependencies.

Run `./RunUnitTests64.bat` in command window to run unit tests.

Run `./Run64.bat` in command window to run `poe_exp_after_dot` locally without install.

Run `./Build64.bat` in command window to build the distribution.

Run `./Clean.bat` in command window to clean temporal data.











