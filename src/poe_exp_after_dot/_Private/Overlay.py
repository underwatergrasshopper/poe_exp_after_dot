import os
import sys
import ctypes
import re

from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass
from copy import deepcopy as _deepcopy

from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent
from PySide6.QtGui      import QColor, QMouseEvent, QIcon, QAction, QCloseEvent, QContextMenuEvent, QFocusEvent, QFont, QEnterEvent, QKeyEvent

from .ErrorBoard        import ErrorBoard
from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels
from .Logic             import Logic, PosData
from .LogManager        import to_log_manager, to_logger
from .Settings          import Settings

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
            [bold]

        Only not skipped values will override font properties from settings. 

        Examples
            --font="Courier New,16,bold"
            --font=",14,"
            --font="Arial,,"
    --custom="<info_board>;<click_bar>;<in_game_exp_bar>;<in_game_exp_tooltip>"
        <info_board>
            [<x>],[<bottom>]
        <click_bar>
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
* - Wildcard

font.name
    Quoted text.
font.size
    Natural number.
font.is_bold
    true
    false
time_max_unit
    "second"
    "minute"
    "hour"
    "day"
    "week"
pos_data.*.*
    Integer number.
""".strip("\n")


class ExpBar(QWidget):
    _logic          : Logic

    _width          : int
    _click_bar      : "ClickBar"

    def __init__(self, logic : Logic, click_bar : "ClickBar"):
        super().__init__()

        self._logic = logic
        self._click_bar = click_bar

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        self.setWindowOpacity(0.5)

        # background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(127, 127, 255))
        self.setPalette(palette)
        
        self.resize_area(0.0, is_try_show = False)

    def resize_area(self, fractional_of_progress : float, *, is_try_show = True):
        """
        ratio
            Value from range 0 to 1.
        """
        pos_data = self._logic.to_pos_data()

        self._width = int(pos_data.in_game_exp_bar_width * fractional_of_progress)

        self.setGeometry(QRect(
            pos_data.in_game_exp_bar_x,
            pos_data.in_game_exp_bar_y,
            max(1, self._width),
            pos_data.in_game_exp_bar_height
        ))

        if is_try_show:
            if self._width >= 1:
                self.show()
            else:
                self.hide()

    def try_show(self):
        if self._width >= 1:
            self.show()

    def mousePressEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            _move_window_to_foreground("Path of Exile")
      
            pos_in_screen = self.mapToGlobal(QPoint(event.x(), event.y()))

            self._click_bar.measure(pos_in_screen.x(), pos_in_screen.y())


class ClickBar(QWidget):
    _logic              : Logic
    _info_board         : "InfoBoard"
    _exp_bar            : ExpBar | None

    def __init__(self, logic : Logic, info_board : "InfoBoard"):
        super().__init__()

        self._logic             = logic
        self._info_board        = info_board
        self._exp_bar           = None

        self._is_first_measure = True

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        self.setWindowOpacity(0.01)

        self.setGeometry(QRect(
            logic.to_pos_data().click_bar_x,
            logic.to_pos_data().click_bar_y,
            logic.to_pos_data().click_bar_width,
            logic.to_pos_data().click_bar_height,
        ))

    def attach_exp_bar(self, exp_bar : ExpBar):
        self._exp_bar = exp_bar

    def mousePressEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            _move_window_to_foreground("Path of Exile")
      
            pos_in_screen = self.mapToGlobal(QPoint(event.x(), event.y()))

            self.measure(pos_in_screen.x(), pos_in_screen.y())

    def measure(self, cursor_x_in_screen : int, cursor_y_in_screen : int):
        self._logic.measure(cursor_x_in_screen, cursor_y_in_screen, [self._info_board])

        if self._is_first_measure:
            self._info_board.place_text(self._logic.gen_exp_info_text(is_control = True), is_lock_left_bottom = True, is_resize = True)
            self._is_first_measure = False

        self._info_board.place_text(self._logic.gen_exp_info_text(), is_lock_left_bottom = True)

        progress = self._logic.to_measurer().get_progress()
        fractional_of_progress = progress - int(progress)

        if self._exp_bar:
            self._exp_bar.resize_area(fractional_of_progress)

def _move_window_to_foreground(window_name : str):
    user32 = ctypes.windll.user32

    window_handle = user32.FindWindowW(None, window_name)
    if window_handle:
        user32.SetForegroundWindow(window_handle)


class InfoBoard(QMainWindow):
    _exp_bar            : ExpBar
    _click_bar          : ClickBar
    _context_menu       : QMenu | None

    _logic              : Logic
    _prev_pos           : QPoint | None

    _flags_backup       : Qt.WindowType | None

    _is_first_measure   : bool  

    def __init__(self, logic : Logic, font_data : "FontData"):
        """
        font_size
            In pixels.
        """
        super().__init__()

        self._logic = logic
        self._prev_pos = None
        self._context_menu = None

        self._flags_backup = None

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)

        # transparency
        self.setWindowOpacity(0.7)

        # text
        self._label = QLabel("", self)
        self._label.setStyleSheet(f"font: {font_data.size}px {font_data.name}; color: white;")
        # NOTE: This is crucial. Prevents from blocking mouseReleaseEvent in parent widget.
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) 

        self.place_text("Click on in-game exp bar to receive data.<br>Ctrl + Shift + LMB to move this board.", is_resize = True)

        #self.set_description("Click on in-game exp bar to receive data. Ctrl + Shift + LMB to move this board.")

        self._click_bar = ClickBar(logic, self)
        self._exp_bar   = ExpBar(logic, self._click_bar)
        self._click_bar.attach_exp_bar(self._exp_bar)

    def place_text(self, description, *, is_lock_left_bottom = False, is_resize = False):
        if is_resize:
            if is_lock_left_bottom:
                rect = self.geometry()
                x = rect.x()
                bottom = rect.y() + rect.height()
            else:
                x = self._logic.to_pos_data().info_board_x
                bottom = self._logic.to_pos_data().info_board_bottom

            self._label.setWordWrap(False)  
            self._label.setText(description)

            self._label.adjustSize()
            self.resize(self._label.size())
            
            pos = self.pos()
            pos.setX(x)
            pos.setY(bottom - self._label.height())
            self.move(pos)
        else:
            self._label.setWordWrap(True)  
            self._label.setText(description)

    def attach_context_menu(self, context_menu : QMenu):
        self._context_menu = context_menu
        self._flags_backup = self._context_menu.windowFlags()


    def mousePressEvent(self, event : QMouseEvent):
        self._exp_bar.activateWindow()
        self._click_bar.activateWindow()
        self.activateWindow()

        # 'Ctrl + Shift + LMB' to move board (order matter)
        if event.button() == Qt.MouseButton.LeftButton and QApplication.keyboardModifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self._prev_pos = event.globalPos()

        if event.button() == Qt.MouseButton.LeftButton and self._flags_backup and self._context_menu:
            self._context_menu.setWindowFlags(self._flags_backup)

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._prev_pos = None

        if event.button() == Qt.MouseButton.RightButton and self._flags_backup and self._context_menu:
            self._context_menu.setWindowFlags(self._flags_backup | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        
        _move_window_to_foreground("Path of Exile")

    def mouseMoveEvent(self, event : QMouseEvent):
        if self._prev_pos is not None:
            offset = QPoint(event.globalPos() - self._prev_pos)
            if offset:
                self.move(self.x() + offset.x(), self.y() + offset.y())
                self._prev_pos = event.globalPos()

    def contextMenuEvent(self, event : QContextMenuEvent):
        if self._context_menu:
            self._context_menu.exec(event.globalPos())

    def showEvent(self, event):
        self._exp_bar.try_show()
        self._click_bar.show()

    def hideEvent(self, event):
        self._exp_bar.hide()
        self._click_bar.hide()


class TrayMenu(QSystemTrayIcon):
    _info_board         : InfoBoard
    _logic              : Logic

    _menu               : QMenu
    _open_data_folder_action : QAction
    _hide_action        : QAction
    _quit_action        : QAction
    _close_menu_action  : QAction

    _flags_backup       : Qt.WindowType

    def __init__(self, info_board : InfoBoard, logic : Logic):
        super().__init__()

        self._info_board = info_board
        self._logic = logic

        icon_file_name =  os.path.abspath(os.path.dirname(__file__) + "/../assets/icon.png")
        self.setIcon(QIcon(icon_file_name))

        self._menu = QMenu()
        self._flags_backup = self._menu.windowFlags()
        
        self._clear_log_file_action = QAction("Clear Log File")
        def clear_log_file():
            to_log_manager().clear_log_file()
            to_logger().info("Cleared runtime.log.")
            self._menu.setWindowFlags(self._flags_backup)

        self._clear_log_file_action.triggered.connect(clear_log_file)
        self._menu.addAction(self._clear_log_file_action)

        self._open_data_folder_action = QAction("Open Data Folder")
        def open_data_folder():
            os.startfile(self._logic.to_settings().get_val("data_path", str))
            self._menu.setWindowFlags(self._flags_backup)

        self._open_data_folder_action.triggered.connect(open_data_folder)
        self._menu.addAction(self._open_data_folder_action)

        self._hide_action = QAction("Hide", checkable = True) # type: ignore
        def hide_overlay(is_hide):
            if is_hide:
                info_board.hide()
            else:
                info_board.show()
            self._menu.setWindowFlags(self._flags_backup)

        self._hide_action.triggered.connect(hide_overlay)
        self._menu.addAction(self._hide_action)

        self._menu.addSeparator()

        self._close_menu_action = QAction("Close Menu")
        self._close_menu_action.triggered.connect(self._menu.close)
        self._menu.addAction(self._close_menu_action)

        self._quit_action = QAction("Quit")
        self._quit_action.triggered.connect(to_app().quit)
        self._menu.addAction(self._quit_action)

        self.setContextMenu(self._menu)

        self._info_board.attach_context_menu(self._menu)


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

            click_bar_x                     : int | None    = None,
            click_bar_y                     : int | None    = None,
            click_bar_width                 : int | None    = None,
            click_bar_height                : int | None    = None,

            in_game_exp_bar_x               : int | None    = None,
            in_game_exp_bar_y               : int | None    = None,
            in_game_exp_bar_width           : int | None    = None,
            in_game_exp_bar_height          : int | None    = None,

            in_game_exp_tooltip_x_offset    : int | None    = None,
            in_game_exp_tooltip_y           : int | None    = None,
            in_game_exp_tooltip_width       : int | None    = None,
            in_game_exp_tooltip_height      : int | None    = None,
                ) -> int:
        """
        Returns
            Exit code.
        """
        if data_path is None:
            data_path = os.environ["APPDATA"] + "/../Local/poe_exp_after_dot"
        data_path = os.path.abspath(data_path)

        os.makedirs(data_path, exist_ok = True)

        to_log_manager().setup_logger(data_path + "/runtime.log", is_debug = is_debug, is_stdout = True)
        
        to_logger().info("====== NEW RUN ======")
        to_logger().debug(f"data_path={data_path}")

        settings = Settings(data_path + "/settings.json", {
            "font" : {
                "name" : "Consolas",
                "size" : 16,
                "is_bold" : False
            },
            "time_max_unit" : "hour",
            "pos_data" : {
                "1920x1080" : {
                    "info_board_x"      : 551,
                    "info_board_bottom" : 1056,

                    "click_bar_x"       : 551,
                    "click_bar_y"       : 1059,
                    "click_bar_width"   : 820,
                    "click_bar_height"  : 21,

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
        temporal_settings = {
            "data_path" : data_path
        }
        if font_data is not None:
            font_settings = {}
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
        _custom_pos_data = temporal_settings["pos_data"]["_command_line_custom"]

        if info_board_x:                    _custom_pos_data["info_board_x"]                    = info_board_x
        if info_board_bottom:               _custom_pos_data["info_board_bottom"]               = info_board_bottom

        if click_bar_x:                     _custom_pos_data["click_bar_x"]                     = click_bar_x
        if click_bar_y:                     _custom_pos_data["click_bar_y"]                     = click_bar_y
        if click_bar_width:                 _custom_pos_data["click_bar_width"]                 = click_bar_width
        if click_bar_height:                _custom_pos_data["click_bar_height"]                = click_bar_height

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

        logic = Logic(settings)

        ErrorBoard.set_default_pos(
            x = logic.to_pos_data().click_bar_x,
            bottom = logic.to_pos_data().click_bar_y,
        )

        app = to_app() # initializes global QApplication object

        font_data = FontData(
            name = settings.get_val("font.name", str),
            size = settings.get_val("font.size", int),
            is_bold = settings.get_val("font.is_bold", bool),
        )
        font_style = "bold" if font_data.is_bold else "normal"
        to_logger().info(f"Font: {font_data.name}, {font_data.size}px, {font_style}.")

        info_board = InfoBoard(logic, font_data = font_data)
        tray_menu = TrayMenu(info_board, logic)

        info_board.show()
        tray_menu.show()

        def excepthook(exception_type, exception : BaseException, traceback_type):
            _exception_stash.exception = exception
            # NOTE: With some brief testing, closeEvent was not triggered when exited with _EXIT_FAILURE (or value equal 1). 
            # But for safety, do not implement closeEvent in any widget.
            QApplication.exit(EXIT_FAILURE)

        previous_excepthook = sys.excepthook
        sys.excepthook = excepthook

        exit_code = to_app().exec_()

        sys.excepthook = previous_excepthook

        del app

        if _exception_stash.exception:
            raise _exception_stash.exception
        
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

        click_bar_x                     : int | None    = None
        click_bar_y                     : int | None    = None
        click_bar_width                 : int | None    = None
        click_bar_height                : int | None    = None

        in_game_exp_bar_x               : int | None    = None
        in_game_exp_bar_y               : int | None    = None
        in_game_exp_bar_width           : int | None    = None
        in_game_exp_bar_height          : int | None    = None

        in_game_exp_tooltip_x_offset    : int | None    = None
        in_game_exp_tooltip_y           : int | None    = None
        in_game_exp_tooltip_width       : int | None    = None
        in_game_exp_tooltip_height      : int | None    = None


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
                    pass

                case ["--time-max-unit", time_max_unit]:
                    if time_max_unit not in ["second", "minute", "hour", "day", "week"]:
                        raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" have unknown value.")

                case ["--font", font_data_text]:
                    name_format = r"(|[^,]+)"
                    size_format = r"(|0|[1-9][0-9]*)"
                    style_format = r"(|bold)"
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

                        click_bar_x                     = next_group()
                        click_bar_y                     = next_group()
                        click_bar_width                 = next_group()
                        click_bar_height                = next_group()

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
                
                ### incorrect ###

                case ["--help" | "-h" | "--debug" | "--settings-help", _]:
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

                click_bar_x                     = click_bar_x,
                click_bar_y                     = click_bar_y,
                click_bar_width                 = click_bar_width,
                click_bar_height                = click_bar_height,

                in_game_exp_bar_x               = in_game_exp_bar_x,
                in_game_exp_bar_y               = in_game_exp_bar_y,
                in_game_exp_bar_width           = in_game_exp_bar_width,
                in_game_exp_bar_height          = in_game_exp_bar_height,

                in_game_exp_tooltip_x_offset    = in_game_exp_tooltip_x_offset,
                in_game_exp_tooltip_y           = in_game_exp_tooltip_y,
                in_game_exp_tooltip_width       = in_game_exp_tooltip_width,
                in_game_exp_tooltip_height      = in_game_exp_tooltip_height
            )
        return EXIT_SUCCESS
