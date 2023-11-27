import os
import sys
import ctypes
import re
import enum
import gc
import shutil

from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass
from copy import deepcopy as _deepcopy

from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QWidgetAction, QLineEdit
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent, QLine, QTimer
from PySide6.QtGui      import QColor, QMouseEvent, QIcon, QAction, QCloseEvent, QContextMenuEvent, QFocusEvent, QFont, QEnterEvent, QKeyEvent, QPainter, QWheelEvent, QActionGroup

from .Commons               import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
from .Logic                 import Logic, PosData
from .LogManager            import to_log_manager, to_logger
from .Settings              import Settings
from .TextGenerator         import TextGenerator, TemplateLoader
from .CharacterRegister     import CharacterRegister, Character

from .GUI.ControlRegion     import ControlRegion
from .GUI.TrayMenu          import TrayMenu

_HELP_TEXT = """
poe_exp_after_dot.py [<option> ...]

<option>
    --help | -h
        Just displays this information. 
        Application won't run.
    --settings-help
        Display information about possible values in settings.json. 
        Application won't run.
    --data-path=<path>
        Relative or absolute path to data folder. 
        In that folder are stored: settings, logs, exp data and other data.
    --font="<name>,<size>,<style>"
        <name>
            Font name.
        <size>
            Size of font in pixels. Only positive integers are allowed.
        <style>
            normal
            bold

        Only not skipped values will override font properties from settings. 

        Examples
            --font="Courier New,16,bold"
            --font=",14,"
            --font="Arial,,"
    --custom="<info_board>;<control_region>;<in_game_exp_bar>;<in_game_exp_tooltip>"
        <info_board>
            [<x>],[<bottom>]
        <control_region>
            [<x>],[<y>],[<width>],[<height>]
        <in_game_exp_bar>
            [<x>],[<y>],[<width>],[<height>]
        <in_game_exp_tooltip>
            [<x_offset>],[<y>],[<width>],[<height>]
        <x_offset>
            Offset on X axis from cursor position.

        Custom position data for overlay elements and game gui elements.
        Only not skipped values will override position data from settings. 

        Examples
            --custom="10,100;,,,;,,,;,,,"
    --time-max-unit=<unit>
        <unit>
            second
            minute
            hour
            day
            week

        Sets max time unit for displaying time in info board.

        Examples
            --time-max-unit=hour
""".strip("\n")

_SETTINGS_HELP_TEXT = """
font.name 
    <text>
font.size
    <natural>                       # in pixels
font.is_bold
    <boolean>
time_max_unit
    "second"
    "minute"
    "hour"
    "day"
    "week"
pos_data.<resolution>.*_x
pos_data.<resolution>.*_x_offset
pos_data.<resolution>.*_y
pos_data.<resolution>.*_bottom
    <integer>                       # in pixels
pos_data.<resolution>.*_width
pos_data.<resolution>.*_height
    <natural>                       # in pixels

<boolean>
    true
    false
""".strip("\n")

# path to top level package
_base_path = os.path.abspath(os.path.dirname(__file__) + "/..")

class _ExceptionStash:
    exception : BaseException | None

    def __init__(self):
        self.exception = None

_exception_stash = _ExceptionStash()


@dataclass
class FontData:
    name        : str | None
    size        : int | None    # in pixels
    is_bold     : bool | None


class Overlay:
    def __init__(self):
        pass

    def run(
            self, 
            *, 
            is_debug        : bool                  = False, 
            font_data       : FontData | None       = None,
            data_path       : str | None            = None, 
            time_max_unit   : str | None            = None,

            info_board_x                    : int | None    = None,
            info_board_bottom               : int | None    = None,

            control_region_x                : int | None    = None,
            control_region_y                : int | None    = None,
            control_region_width            : int | None    = None,
            control_region_height           : int | None    = None,

            in_game_exp_bar_x               : int | None    = None,
            in_game_exp_bar_y               : int | None    = None,
            in_game_exp_bar_width           : int | None    = None,
            in_game_exp_bar_height          : int | None    = None,

            in_game_exp_tooltip_x_offset    : int | None    = None,
            in_game_exp_tooltip_y           : int | None    = None,
            in_game_exp_tooltip_width       : int | None    = None,
            in_game_exp_tooltip_height      : int | None    = None,

            is_overwrite_default_format     : bool          = False,
                ) -> int:
        """
        Returns
            Exit code.
        """
        if data_path is None:
            data_path = get_default_data_path()

        os.makedirs(data_path, exist_ok = True)

        to_log_manager().setup_logger(data_path + "/runtime.log", is_debug = is_debug, is_stdout = True)
        
        to_logger().info("====== NEW RUN ======")
        to_logger().debug(f"data_path={data_path}")

        settings = Settings(data_path + "/settings.json", {
            "_comment" : "Type 'py -3-64 poe_exp_after_dot.py --settings-help' in console to see possible values.",
            "font" : {
                "name" : "Consolas",
                "size" : 16,
                "is_bold" : False
            },
            "character_name" : "",
            "time_max_unit" : "hour",
            "pos_data" : {
                "1920x1080" : {
                    "info_board_x"      : 551,
                    "info_board_bottom" : 1056,

                    "control_region_x"       : 551,
                    "control_region_y"       : 1059,
                    "control_region_width"   : 820,
                    "control_region_height"  : 21,

                    "in_game_exp_bar_x"         : 551,
                    "in_game_exp_bar_y"         : 1069,
                    "in_game_exp_bar_width"     : 820,
                    "in_game_exp_bar_height"    : 5,

                    "in_game_exp_tooltip_x_offset"  : 64,
                    "in_game_exp_tooltip_y"         : 1007,
                    "in_game_exp_tooltip_width"     : 446,
                    "in_game_exp_tooltip_height"    : 73,
                }
            }
        })

        temporal_settings : dict[str, Any] = {
            "data_path" : data_path,
            "is_debug" : is_debug,
        }
        if font_data is not None:
            font_settings : dict[str, Any] = {}
            if font_data.name is not None:
                font_settings["name"] = font_data.name
            if font_data.size is not None:
                font_settings["size"] = font_data.size
            if font_data.is_bold is not None:
                font_settings["is_bold"] = font_data.is_bold

            temporal_settings["font"] = font_settings

        if time_max_unit is not None:
            temporal_settings["time_max_unit"] = time_max_unit

        temporal_settings.update(merge_on_all_levels(temporal_settings, {"pos_data" : {"_command_line_custom" : {}}}))
        _custom_pos_data : dict[str, Any] = temporal_settings["pos_data"]["_command_line_custom"]

        if info_board_x:                    _custom_pos_data["info_board_x"]                    = info_board_x
        if info_board_bottom:               _custom_pos_data["info_board_bottom"]               = info_board_bottom

        if control_region_x:                _custom_pos_data["control_region_x"]                = control_region_x
        if control_region_y:                _custom_pos_data["control_region_y"]                = control_region_y
        if control_region_width:            _custom_pos_data["control_region_width"]            = control_region_width
        if control_region_height:           _custom_pos_data["control_region_height"]           = control_region_height

        if in_game_exp_bar_x:               _custom_pos_data["in_game_exp_bar_x"]               = in_game_exp_bar_x
        if in_game_exp_bar_y:               _custom_pos_data["in_game_exp_bar_y"]               = in_game_exp_bar_y
        if in_game_exp_bar_width:           _custom_pos_data["in_game_exp_bar_width"]           = in_game_exp_bar_width
        if in_game_exp_bar_height:          _custom_pos_data["in_game_exp_bar_height"]          = in_game_exp_bar_height

        if in_game_exp_tooltip_x_offset:    _custom_pos_data["in_game_exp_tooltip_x_offset"]    = in_game_exp_tooltip_x_offset
        if in_game_exp_tooltip_y:           _custom_pos_data["in_game_exp_tooltip_y"]           = in_game_exp_tooltip_y
        if in_game_exp_tooltip_width:       _custom_pos_data["in_game_exp_tooltip_width"]       = in_game_exp_tooltip_width
        if in_game_exp_tooltip_height:      _custom_pos_data["in_game_exp_tooltip_height"]      = in_game_exp_tooltip_height

        to_logger().debug(f"temporal_settings={temporal_settings}")

        settings.load_and_add_temporal(temporal_settings)

        to_logger().info("Loaded settings.")

        def_format_file_name = data_path + "/formats/Default.format"
        settings.set_val("def_format_file_name", def_format_file_name, str, is_temporal_only = True)

        if not os.path.exists(def_format_file_name) or is_overwrite_default_format:
            os.makedirs(os.path.dirname(def_format_file_name), exist_ok = True)

            if is_overwrite_default_format and os.path.exists(def_format_file_name):
                os.remove(def_format_file_name)

            source_file_name = _base_path + "/assets/Default.format"
            
            shutil.copy(source_file_name, def_format_file_name)

            to_logger().info("Created \"Default.format\".")

        logic = Logic(settings)

        logic.scan_and_load_character()

        app = to_app() # initializes global QApplication object

        font_data = FontData(
            name = settings.get_val("font.name", str),
            size = settings.get_val("font.size", int),
            is_bold = settings.get_val("font.is_bold", bool),
        )
        font_style = "bold" if font_data.is_bold else "normal"
        to_logger().info(f"Font: {font_data.name}, {font_data.size}px, {font_style}.")

        app.setStyle("Fusion")

        control_region  = ControlRegion(logic)
        tray_menu       = TrayMenu(control_region.to_menu())

        tray_menu.show()
        control_region.start_foreground_guardian()
        
        # raise RuntimeError("Some error.") # debug

        def excepthook(exception_type, exception : BaseException, traceback_type):
            _exception_stash.exception = exception
            # NOTE: With some brief testing, closeEvent was not triggered when exited with EXIT_FAILURE (or value equal 1). 
            # But for safety, do not implement closeEvent in any widget.

            # Workaround. To prevent any widget to be visible while exception is processed.
            for widget in to_app().allWidgets():
                widget.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
                widget.setDisabled(True)
                widget.hide()

            QApplication.exit(EXIT_FAILURE)

        previous_excepthook = sys.excepthook
        sys.excepthook = excepthook

        to_logger().info(f"Running.")
        exit_code = to_app().exec()

        sys.excepthook = previous_excepthook

        if _exception_stash.exception:
            exception = _exception_stash.exception
            _exception_stash.exception = None
            raise exception
        
        logic.save_character()
    
        settings.save()
        to_logger().info("Saved settings.")

        to_logger().info("Exit.")
        
        return exit_code

    def main(self, argv : list[str]) -> int:
        """
        Returns
            Exit code.
        Exceptions
            ValueError
                When any given option in argument list is incorrect
        """
        ### parses command line options ###
        is_run                                          = True
        is_debug                                        = False
        font_data           : FontData | None           = None
        raw_custom_pos_data : str | None                = None
        data_path           : str | None                = None
        time_max_unit       : str | None                = None

        info_board_x                    : int | None    = None
        info_board_bottom               : int | None    = None

        control_region_x                     : int | None    = None
        control_region_y                     : int | None    = None
        control_region_width                 : int | None    = None
        control_region_height                : int | None    = None

        in_game_exp_bar_x               : int | None    = None
        in_game_exp_bar_y               : int | None    = None
        in_game_exp_bar_width           : int | None    = None
        in_game_exp_bar_height          : int | None    = None

        in_game_exp_tooltip_x_offset    : int | None    = None
        in_game_exp_tooltip_y           : int | None    = None
        in_game_exp_tooltip_width       : int | None    = None
        in_game_exp_tooltip_height      : int | None    = None

        is_overwrite_default_format                     = False


        for argument in argv[1:]:
            option_name, *value = argument.split("=", 1)

            match (option_name, *value):
                ### correct ###

                case ["--help" | "-h"]:
                    print(_HELP_TEXT)
                    is_run = False

                case ["--settings-help"]:
                    print(_SETTINGS_HELP_TEXT)
                    is_run = False

                case ["--debug"]:
                    is_debug = True

                case ["--data-path", data_path]:
                    data_path = data_path.lstrip("/").lstrip("\\").lstrip("\\")

                case ["--time-max-unit", time_max_unit]:
                    if time_max_unit not in ["second", "minute", "hour", "day", "week"]:
                        raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" have unknown value.")

                case ["--font", font_data_text]:
                    name_format = r"(|[^,]+)"
                    size_format = r"(|0|[1-9][0-9]*)"
                    style_format = r"(|normal|bold)"
                    match_ = re.search(fr"^{name_format},{size_format},{style_format}$", font_data_text)
                    if match_:
                        font_data = FontData(
                            name               = match_.group(1) if match_.group(1) else None,
                            size               = int(match_.group(2)),
                            is_bold            = match_.group(3) == "bold",
                        )
                    else:
                        raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" have wrong format.")

                case ["--custom", raw_custom_pos_data]:
                    n = r"(|0|[1-9][0-9]*)"
                    match_ = re.search(fr"^{n},{n};{n},{n},{n},{n};{n},{n},{n},{n};{n},{n},{n},{n}$", raw_custom_pos_data)
                    if match_:
                        index = 1
                        def next_group():
                            nonlocal index
                            group = match_.group(index)
                            index += 1
                            return int(group) if group else None
                        
                        info_board_x                    = next_group()
                        info_board_bottom               = next_group()

                        control_region_x                     = next_group()
                        control_region_y                     = next_group()
                        control_region_width                 = next_group()
                        control_region_height                = next_group()

                        in_game_exp_bar_x               = next_group()
                        in_game_exp_bar_y               = next_group()
                        in_game_exp_bar_width           = next_group()
                        in_game_exp_bar_height          = next_group()

                        in_game_exp_tooltip_x_offset    = next_group()
                        in_game_exp_tooltip_y           = next_group()
                        in_game_exp_tooltip_width       = next_group()
                        in_game_exp_tooltip_height      = next_group()
                        

                    else:
                        raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" have wrong format.")
                
                case ["--overwrite-default-format"]:
                    is_overwrite_default_format = True

                ### incorrect ###

                case ["--help" | "-h" | "--debug" | "--settings-help" | "--overwrite-default-format", _]:
                    raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" can't have a value.")
                
                case ["--data-path" | "--custom" | "--font" | "--time-max-unit"]:
                    raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" need to have a value.")

                case [option_name, *_]:
                    raise ValueError(f"Incorrect command line argument. Unknown option \"{option_name}\".")
        
        if is_run:
            return self.run(
                is_debug                        = is_debug,
                font_data                       = font_data,
                data_path                       = data_path,
                time_max_unit                   = time_max_unit,

                info_board_x                    = info_board_x,
                info_board_bottom               = info_board_bottom,

                control_region_x                     = control_region_x,
                control_region_y                     = control_region_y,
                control_region_width                 = control_region_width,
                control_region_height                = control_region_height,

                in_game_exp_bar_x               = in_game_exp_bar_x,
                in_game_exp_bar_y               = in_game_exp_bar_y,
                in_game_exp_bar_width           = in_game_exp_bar_width,
                in_game_exp_bar_height          = in_game_exp_bar_height,

                in_game_exp_tooltip_x_offset    = in_game_exp_tooltip_x_offset,
                in_game_exp_tooltip_y           = in_game_exp_tooltip_y,
                in_game_exp_tooltip_width       = in_game_exp_tooltip_width,
                in_game_exp_tooltip_height      = in_game_exp_tooltip_height,

                is_overwrite_default_format     = is_overwrite_default_format
            )
        return EXIT_SUCCESS
