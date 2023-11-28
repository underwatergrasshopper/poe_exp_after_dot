import os       as _os
import sys      as _sys
import re       as _re
import shutil   as _shutil

from typing         import Any, Type
from dataclasses    import dataclass

from PySide6.QtWidgets  import QApplication
from PySide6.QtCore     import Qt

from .Commons               import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
from .Logic                 import Logic
from .LogManager            import to_log_manager, to_logger
from .Settings              import Settings

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
    <natural> # in pixels
font.is_bold
    <boolean>
character_name
    <text>
time_max_unit
    "second"
    "minute"
    "hour"
    "day"
    "week"
selected_pos_data_name
    <text>
pos_data.<resolution>.info_board_x
    <integer> # in pixels
pos_data.<resolution>.info_board_bottom
    <integer> # in pixels
pos_data.<resolution>.control_region_x
    <integer> # in pixels
pos_data.<resolution>.control_region_y
    <integer> # in pixels
pos_data.<resolution>.control_region_width
    <natural> # in pixels
pos_data.<resolution>.control_region_height
    <natural> # in pixels
pos_data.<resolution>.in_game_exp_bar_x
    <integer> # in pixels
pos_data.<resolution>.in_game_exp_bar_y
    <integer> # in pixels
pos_data.<resolution>.in_game_exp_bar_width
    <natural> # in pixels
pos_data.<resolution>.in_game_exp_bar_height
    <natural> # in pixels
pos_data.<resolution>.in_game_exp_tooltip_x_offset
    <integer> # in pixels
pos_data.<resolution>.in_game_exp_tooltip_y
    <integer> # in pixels
pos_data.<resolution>.in_game_exp_tooltip_width
    <natural> # in pixels
pos_data.<resolution>.in_game_exp_tooltip_height
    <natural> # in pixels

<boolean>
    true
    false
""".strip("\n")

# path to top level package
_base_path = _os.path.abspath(_os.path.dirname(__file__) + "/..")


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

        _os.makedirs(data_path, exist_ok = True)

        to_log_manager().setup_logger(data_path + "/runtime.log", is_debug = is_debug, is_stdout = True)
        
        to_logger().info("====== NEW RUN ======")
        to_logger().debug(f"data_path={data_path}")

        settings = Settings()

        ### default settings ###

        settings.merge_with({
            "_comment_help" : ["Type 'py -3-64 poe_exp_after_dot.py --settings-help' in console to see this info.", ""] + _SETTINGS_HELP_TEXT.split("\n"),
            "font" : {
                "name" : "Consolas",
                "size" : 16,
                "is_bold" : False
            },
            "character_name" : "",
            "time_max_unit" : "hour",
            "selected_pos_data_name" : "1920x1080",
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

        ### load settings ###

        settings_path = data_path + "/settings.json"
        settings.load(settings_path)
        to_logger().info("Loaded settings.")

        ### temporal settings ###

        settings.set_tmp_val("data_path", data_path, str)
        settings.set_tmp_val("is_debug", is_debug, bool)

        if font_data is not None:
            settings.set_tmp_val("font.name", font_data.name, str)
            settings.set_tmp_val("font.size", font_data.size, int)
            settings.set_tmp_val("font.is_bold", font_data.is_bold, bool)

        if time_max_unit is not None:
            settings.set_tmp_val("font.time_max_unit", time_max_unit, int)

        selected_pos_data_name = settings.get_val("selected_pos_data_name", str)

        def solve_pos_data(parameter : Any, name : str, value_type : Type):
            if parameter is not None: 
                settings.set_tmp_val(f"_solved_pos_data.{name}", parameter, value_type) 
            else:
                settings.copy_tmp_val(f"pos_data.{selected_pos_data_name}.{name}", f"_solved_pos_data.{name}") 

        solve_pos_data(info_board_x,                    "info_board_x", int)
        solve_pos_data(info_board_bottom,               "info_board_bottom", int)

        solve_pos_data(control_region_x,                "control_region_x", int)
        solve_pos_data(control_region_y,                "control_region_y", int)
        solve_pos_data(control_region_width,            "control_region_width", int)
        solve_pos_data(control_region_height,           "control_region_height", int)

        solve_pos_data(in_game_exp_bar_x,               "in_game_exp_bar_x", int)
        solve_pos_data(in_game_exp_bar_y,               "in_game_exp_bar_y", int)
        solve_pos_data(in_game_exp_bar_width,           "in_game_exp_bar_width", int)
        solve_pos_data(in_game_exp_bar_height,          "in_game_exp_bar_height", int)

        solve_pos_data(in_game_exp_tooltip_x_offset,    "in_game_exp_tooltip_x_offset", int)
        solve_pos_data(in_game_exp_tooltip_y,           "in_game_exp_tooltip_y", int)
        solve_pos_data(in_game_exp_tooltip_width,       "in_game_exp_tooltip_width", int)
        solve_pos_data(in_game_exp_tooltip_height,      "in_game_exp_tooltip_height", int)
    
        def_format_file_name = data_path + "/formats/Default.format"
        settings.set_tmp_val("def_format_file_name", def_format_file_name, str)

        to_logger().debug(f"temporal_settings={settings.to_temporal()}")

        _try_create_default_format_file(def_format_file_name, is_overwrite_default_format)

        logic = Logic(settings)

        logic.scan_and_load_character()

        app = to_app() # initializes global QApplication object

        to_logger().info(_get_font_info(settings))

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

        previous_excepthook = _sys.excepthook
        _sys.excepthook = excepthook

        to_logger().info(f"Running.")
        exit_code = to_app().exec()

        _sys.excepthook = previous_excepthook

        if _exception_stash.exception:
            exception = _exception_stash.exception
            _exception_stash.exception = None
            raise exception
        
        logic.save_character()
    
        settings.save(settings_path)
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
                    match_ = _re.search(fr"^{name_format},{size_format},{style_format}$", font_data_text)
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
                    match_ = _re.search(fr"^{n},{n};{n},{n},{n},{n};{n},{n},{n},{n};{n},{n},{n},{n}$", raw_custom_pos_data)
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


def _get_font_info(settings : Settings) -> str:
    name = settings.get_val("font.name", str)
    size = settings.get_val("font.size", int)
    is_bold = settings.get_val("font.is_bold", bool)
 
    style = "bold" if is_bold else "normal"

    return f"Font: {name}, {size}px, {style}."


def _try_create_default_format_file(def_format_file_name : str, is_overwrite_default_format : bool):
    if not _os.path.exists(def_format_file_name) or is_overwrite_default_format:
        _os.makedirs(_os.path.dirname(def_format_file_name), exist_ok = True)

        if is_overwrite_default_format and _os.path.exists(def_format_file_name):
            _os.remove(def_format_file_name)

        source_file_name = _base_path + "/assets/Default.format"
        
        _shutil.copy(source_file_name, def_format_file_name)

        to_logger().info("Created \"Default.format\".")