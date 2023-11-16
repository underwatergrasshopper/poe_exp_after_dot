import os
import sys
import ctypes
import re
import enum
import gc

from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass
from copy import deepcopy as _deepcopy

from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent, QLine, QTimer
from PySide6.QtGui      import QColor, QMouseEvent, QIcon, QAction, QCloseEvent, QContextMenuEvent, QFocusEvent, QFont, QEnterEvent, QKeyEvent, QPainter

from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
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


class InfoBoard(QWidget):
    _logic : Logic

    def __init__(self, logic : Logic):
        """
        font_size
            In pixels.
        """
        super().__init__()

        self._logic = logic

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.WindowTransparentForInput
        )

        # transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        font_name = logic.to_settings().get_val("font.name", str)
        font_size = logic.to_settings().get_val("font.size", int) # in pixels
        is_bold = logic.to_settings().get_val("font.is_bold", bool)
        font_wight = "bold" if is_bold else "normal"

        # text
        self._label = QLabel("", self)
        self._label.setStyleSheet(f"font: {font_wight} {font_size}px {font_name}; color: white;")

        # default message
        self.place_text("Hover over exp bar area to show details.<br>Click to dismiss this message.", is_resize = True)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(1.0)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 127))

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


class FracExpBar(QWidget):
    _logic          : Logic

    _base_width     : int
    _step_width     : int
    _progress_width : int

    def __init__(self, logic : Logic):
        super().__init__()

        self._logic = logic

        self._base_width        = 0
        self._step_width        = 0
        self._progress_width    = 0

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.WindowTransparentForInput
        )

        pos_data = self._logic.to_pos_data()

        self.setGeometry(QRect(
            pos_data.in_game_exp_bar_x,
            pos_data.in_game_exp_bar_y,
            pos_data.in_game_exp_bar_width,
            pos_data.in_game_exp_bar_height
        ))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.update_bar(0.0, 0.0, is_try_show = False)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        painter.fillRect(QRect(rect.left(), rect.top(), self._base_width, rect.height()), QColor(127, 127, 255, 95))
        painter.fillRect(QRect(self._base_width, rect.top(), self._step_width, rect.height()), QColor(127, 255, 255, 95))

    def update_bar(self, progress : float, progress_step : float, *, is_try_show = True):
        """
        progress
            In percent.
        progress_step
            In percent.
        """
        pos_data = self._logic.to_pos_data()

        previous_progress_width = self._progress_width
        frac_progress = progress % 1
        progress_width = int((pos_data.in_game_exp_bar_width * frac_progress) // 1)

        if previous_progress_width > progress_width or progress_step > 1.0:
            # next level, next 1% or other character
            self._base_width = 0
            self._step_width = progress_width
        else:
            self._base_width = previous_progress_width
            self._step_width = progress_width - previous_progress_width

        self._progress_width = self._base_width + self._step_width

        self.repaint()

        if is_try_show:
            if self._progress_width >= 1:
                self.show()
            else:
                self.hide()

    def try_show(self):
        if self._progress_width >= 1:
            self.show()

class Menu(QMenu):
    _logic                      : Logic
    _control_region             : "ControlRegion"   # reference

    _clear_log_file_action      : QAction
    _open_data_folder_action    : QAction
    _hide_action                : QAction
    _enable_debug_action        : QAction
    _quit_action                : QAction
    _close_menu_action          : QAction

    _title                      : QAction
    _flags_backup               : Qt.WindowType

    def __init__(self, logic : Logic, control_region : "ControlRegion"):
        super().__init__()

        self._logic = logic
        self._control_region = control_region

        self._title = self.addAction("poe exp after dot")
        self._title.setEnabled(False)
        self.addSeparator()

        self._flags_backup = self.windowFlags()
        
        self._clear_log_file_action = QAction("Clear Log File")
        def clear_log_file():
            to_log_manager().clear_log_file()
            to_logger().info("Cleared runtime.log.")
            self.setWindowFlags(self._flags_backup)         

        self._clear_log_file_action.triggered.connect(clear_log_file)
        self.addAction(self._clear_log_file_action)

        self._open_data_folder_action = QAction("Open Data Folder")
        def open_data_folder():
            os.startfile(self._logic.to_settings().get_val("data_path", str))
            self.setWindowFlags(self._flags_backup)

        self._open_data_folder_action.triggered.connect(open_data_folder)
        self.addAction(self._open_data_folder_action)

        self._hide_action = QAction("Hide Overlay", checkable = True) # type: ignore
        def hide_overlay(is_hide):
            if is_hide:
                self._control_region.pause_foreground_guardian_and_hide()
            else:
                self._control_region.resume_foreground_guardian()
            self.setWindowFlags(self._flags_backup)

        self._hide_action.triggered.connect(hide_overlay)
        self.addAction(self._hide_action)

        self._enable_debug_action = QAction("Enable Debug", checkable = True) # type: ignore
        self._enable_debug_action.setChecked(self._logic.to_settings().get_val("is_debug", bool))
        def enable_debug(is_enable):
            if is_enable:
                self._logic.to_settings().set_val("is_debug", True, bool)
                to_log_manager().set_is_debug(True)
            else:
                self._logic.to_settings().set_val("is_debug", False, bool)
                to_log_manager().set_is_debug(False)

            self._control_region.repaint()

            self.setWindowFlags(self._flags_backup)

        self._enable_debug_action.triggered.connect(enable_debug)
        self.addAction(self._enable_debug_action)

        self.addSeparator()

        self._close_menu_action = QAction("Close Menu")
        self._close_menu_action.triggered.connect(self.close)
        self.addAction(self._close_menu_action)

        self._quit_action = QAction("Quit")
        self._quit_action.triggered.connect(to_app().quit)
        self.addAction(self._quit_action)


class ForegroundGuardian:
    _control_region : "ControlRegion"
    _user32         : ctypes.WinDLL
    _is_paused      : bool
    _timer          : QTimer

    def __init__(self, control_region : "ControlRegion"):
        self._control_region    = control_region
        self._user32            = ctypes.windll.user32
        self._is_paused         = False

        self._timer = QTimer()
        self._timer.timeout.connect(self._try_change_visibility)
        self._timer.setInterval(500)

    def start(self):
        self._timer.start()

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def is_paused(self) -> bool:
        return self._is_paused

    def _try_change_visibility(self):
        if not self._is_paused:
            window_handle = self._user32.FindWindowW(None, "Path of Exile")
            if window_handle and window_handle == self._user32.GetForegroundWindow():
                self._control_region.show()
            else:
                self._control_region.hide()


class ControlRegion(QMainWindow):
    _logic                  : Logic         # reference
    _info_board             : InfoBoard
    _frac_exp_bar           : FracExpBar
    _menu                   : Menu

    _flags_backup           : Qt.WindowType
    _foreground_guardian    : ForegroundGuardian

    _is_first_measure       : bool  

    def __init__(self, logic : Logic):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setGeometry(QRect(
            logic.to_pos_data().control_region_x,
            logic.to_pos_data().control_region_y,
            logic.to_pos_data().control_region_width,
            logic.to_pos_data().control_region_height,
        ))

        self._logic             = logic

        self._info_board    = InfoBoard(logic)
        self._frac_exp_bar  = FracExpBar(logic)
        self._menu          = Menu(logic, self)

        self._flags_backup = self._menu.windowFlags()
        
        self._foreground_guardian = ForegroundGuardian(self)

        self._is_first_measure  = True

    def to_menu(self) -> Menu:
        return self._menu

    def start_foreground_guardian(self):
        self._foreground_guardian.start()

    def pause_foreground_guardian_and_hide(self):
        self._foreground_guardian.pause()
        self.hide()

    def resume_foreground_guardian(self):
        self._foreground_guardian.resume()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

        if self._logic.to_settings().get_val("is_debug", bool):
            painter.setPen(QColor(0, 255, 0))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
    def mousePressEvent(self, event : QMouseEvent):
        _move_window_to_foreground("Path of Exile")

        if self._menu.isVisible():
            self._menu.close()

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self._menu.setWindowFlags(self._flags_backup | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        elif event.button() == Qt.MouseButton.LeftButton:
            _move_window_to_foreground("Path of Exile")

            pos_in_screen = self.mapToGlobal(QPoint(event.x(), event.y()))

            self._measure(pos_in_screen.x(), pos_in_screen.y())

            self._menu.setWindowFlags(self._flags_backup)
        
        _move_window_to_foreground("Path of Exile")

    def contextMenuEvent(self, event : QContextMenuEvent):
        self._menu.exec(event.globalPos())

    def showEvent(self, event):
        if self._is_first_measure:
            self._info_board.show()

        self._frac_exp_bar.try_show()

    def hideEvent(self, event):
        self._frac_exp_bar.hide()

        if self._is_first_measure:
            self._info_board.hide()

        if self._menu.isVisible():
            self._menu.close()

    def enterEvent(self, event: QEnterEvent):
        if not self._is_first_measure:
            self._info_board.show()

    def leaveEvent(self, event: QEvent):
        if not self._is_first_measure:
            self._info_board.hide()

    def _measure(self, cursor_x_in_screen : int, cursor_y_in_screen : int):
        self._foreground_guardian.pause()
        self._logic.measure(cursor_x_in_screen, cursor_y_in_screen, [self])
        self._foreground_guardian.resume()

        if self._is_first_measure:
            self._info_board.place_text(self._logic.gen_exp_info_text(is_control = True), is_lock_left_bottom = True, is_resize = True)
            self._is_first_measure = False

        self._info_board.place_text(self._logic.gen_exp_info_text(), is_lock_left_bottom = True)

        progress = self._logic.to_measurer().get_progress()
        progress_step = self._logic.to_measurer().get_progress_step()

        self._frac_exp_bar.update_bar(progress, progress_step)


def _move_window_to_foreground(window_name : str):
    user32 = ctypes.windll.user32

    window_handle = user32.FindWindowW(None, window_name)
    if window_handle:
        user32.SetForegroundWindow(window_handle)

class TrayMenu(QSystemTrayIcon):
    def __init__(self, menu : Menu):
        # Do not own 'menu'.
        super().__init__()

        icon_file_name =  os.path.abspath(os.path.dirname(__file__) + "/../assets/icon.png")
        self.setIcon(QIcon(icon_file_name))

        self.setContextMenu(menu)


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
            "is_debug" : is_debug
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

        logic = Logic(settings)

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
        
        raise RuntimeError("Some error.") # debug

        def excepthook(exception_type, exception : BaseException, traceback_type):
            _exception_stash.exception = exception
            # NOTE: With some brief testing, closeEvent was not triggered when exited with _EXIT_FAILURE (or value equal 1). 
            # But for safety, do not implement closeEvent in any widget.
            QApplication.exit(EXIT_FAILURE)

        previous_excepthook = sys.excepthook
        sys.excepthook = excepthook

        to_logger().info(f"Running.")
        exit_code = to_app().exec_()

        sys.excepthook = previous_excepthook

        del app

        if _exception_stash.exception:
            exception = _exception_stash.exception
            _exception_stash.exception = None
            raise exception
        
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
                in_game_exp_tooltip_height      = in_game_exp_tooltip_height
            )
        return EXIT_SUCCESS
