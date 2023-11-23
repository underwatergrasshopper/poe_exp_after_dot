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

from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent, QLine, QTimer
from PySide6.QtGui      import QColor, QMouseEvent, QIcon, QAction, QCloseEvent, QContextMenuEvent, QFocusEvent, QFont, QEnterEvent, QKeyEvent, QPainter, QWheelEvent

from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
from .Logic             import Logic, PosData
from .LogManager        import to_log_manager, to_logger
from .Settings          import Settings
from .TextGenerator     import TextGenerator, TemplateLoader

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

_NOTHING = 0
_CTRL    = Qt.KeyboardModifier.ControlModifier
_SHIFT   = Qt.KeyboardModifier.ShiftModifier
_ALT     = Qt.KeyboardModifier.AltModifier

def _get_key_modifiers():
    mask = _CTRL | _SHIFT | _ALT
    return to_app().keyboardModifiers() & mask

class InfoBoard(QWidget):
    _logic          : Logic
    _is_dismissed   : bool

    def __init__(self, logic : Logic):
        """
        font_size
            In pixels.
        """
        super().__init__()

        self._logic = logic
        self._is_dismissed = False

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        font_name = logic.to_settings().get_val("font.name", str)
        font_size = logic.to_settings().get_val("font.size", int) # in pixels
        is_bold = logic.to_settings().get_val("font.is_bold", bool)
        font_wight = "bold" if is_bold else "normal"

        # text
        self._label = QLabel("", self)
        self._label.setStyleSheet(f"font-weight: {font_wight}; font-size: {font_size}px; font-family: {font_name}; color: white;")

        ### info board text templates ###
        template_loader = TemplateLoader()
        def_format_file_name = logic.to_settings().get_val("def_format_file_name", str)
        to_logger().info(f"Loading formats from \"{os.path.basename(def_format_file_name)}\" ...")
        template_loader.load_and_parse(logic.to_settings().get_val("def_format_file_name", str))
        to_logger().info("Formats has been loaded.")

        for name, value in template_loader.to_variables().items():
            logic.to_settings().set_val(name, value, str)

        self._text_generator = TextGenerator(template_loader.to_templates(), self._logic.get_info_board_text_parameters, self.set_text)
        self._text_generator.start()
        self._text_generator.gen_text("First Help")
        ###

    def set_text_by_template(self, template_name : str):
        self._text_generator.gen_text(template_name)

    def get_current_template_name(self) -> str:
        return self._text_generator.get_current_template_name()

    def dismiss(self):
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        self._is_dismissed = True

    def is_dismissed(self) -> bool:
        return self._is_dismissed

    def set_text(self, text : str):
        x = self._logic.to_pos_data().info_board_x
        bottom = self._logic.to_pos_data().info_board_bottom

        self._label.setWordWrap(False)  
        self._label.setText(text)

        self._label.adjustSize()
        self.resize(self._label.size())
        
        pos = self.pos()
        pos.setX(x)
        pos.setY(bottom - self._label.height())
        self.move(pos)

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide()
            self.dismiss()
            self.set_text_by_template("Just Hint")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(1.0)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 127))


class FracExpBar(QWidget):
    _logic                  : Logic

    _base_width             : int
    _step_width             : int
    _frac_progress_width    : int

    def __init__(self, logic : Logic):
        super().__init__()

        self._logic = logic

        self._base_width            = 0
        self._step_width            = 0
        self._frac_progress_width   = 0

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
        
        self.update_bar_manually(0.0, 0.0, is_try_show = False)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        painter.fillRect(QRect(rect.left(), rect.top(), self._base_width, rect.height()), QColor(127, 127, 255, 95))
        painter.fillRect(QRect(self._base_width, rect.top(), self._step_width, rect.height()), QColor(127, 255, 255, 95))

    def update_bar(self, *, is_try_show = True):
        self.update_bar_manually(self._logic.to_measurer().get_progress(), self._logic.to_measurer().get_progress_step(), is_try_show = is_try_show)

    def update_bar_manually(self, progress : float, progress_step : float, *, is_try_show = True):
        """
        progress
            In percent.
        progress_step
            In percent.
        """
        progress_base = progress - progress_step

        frac_progress_base = progress_base % 1

        gain = frac_progress_base + progress_step

        if gain < 1.0:
            self._base_width = frac_progress_base
            self._step_width = progress_step
        else:
            self._base_width = 0.0
            self._step_width = gain % 1

        width = self._logic.to_pos_data().in_game_exp_bar_width
        self._base_width = int((self._base_width * width) // 1)
        self._step_width = int((self._step_width * width) // 1)

        self._frac_progress_width = self._base_width + self._step_width

        self.repaint()

        if is_try_show:
            if self._frac_progress_width >= 1:
                self.show()
            else:
                self.hide()

    def try_show(self):
        if self._frac_progress_width >= 1:
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
            os.startfile(os.path.abspath(self._logic.to_settings().get_val("data_path", str)))
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
        def quit():
            to_logger().info("Quitting...")
            to_app().quit()
        self._quit_action.triggered.connect(quit)
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
    _is_show_menu           : False

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
        # raise RuntimeError("Some error.") # debug

        _move_window_to_foreground("Path of Exile")

        modifiers = _get_key_modifiers()

        if self._menu.isVisible():
            self._menu.close()

        if not self._info_board.is_dismissed():
            self._info_board.dismiss()

        if event.button() == Qt.MouseButton.LeftButton:
            pass

        elif event.button() == Qt.MouseButton.MiddleButton:
            if self._logic.to_measurer().get_current_entry_page() == 0:
                self._info_board.set_text_by_template("No Entry with Page Header")
            else:
                self._info_board.set_text_by_template("Result with Page Header")
            self._info_board.show()

        elif event.button() == Qt.MouseButton.RightButton:
            if modifiers == _SHIFT:
                self._info_board.set_text_by_template("Help")
                self._info_board.show()
            elif modifiers == _NOTHING:
                self._is_show_menu = True

    def mouseReleaseEvent(self, event : QMouseEvent):
        modifiers = _get_key_modifiers()

        if event.button() == Qt.MouseButton.RightButton:
            if modifiers == _SHIFT:
                self._dismiss_help()
            elif modifiers == _CTRL:
                self._previous_entry()
            elif modifiers == (_CTRL | _SHIFT):
                measurer = self._logic.to_measurer()

                measurer.go_to_before_first_entry()
                self._info_board.set_text_by_template("On No Entry")
                self._info_board.show()
                
                self._frac_exp_bar.update_bar()

            elif self._info_board.get_current_template_name() == "Help":
                # Workaround!!! 
                # Dismiss help in case when Shift was released before RMB.
                # '_move_window_to_foreground' removes keyboard focus, so 'keyReleaseEvent' is not received.
                self._dismiss_help()

            else:
                self._menu.setWindowFlags(self._flags_backup | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
                self._menu.exec(event.globalPos())

        elif event.button() == Qt.MouseButton.LeftButton:
            if modifiers == _CTRL:
                self._next_entry()
            elif modifiers == (_CTRL | _SHIFT):
                measurer = self._logic.to_measurer()

                measurer.go_to_last_entry()
                page = measurer.get_current_entry_page()
                if page == 0:
                    self._info_board.set_text_by_template("On No Entry")
                else:
                    self._info_board.set_text_by_template("On Last")

                self._info_board.show()
                
                self._frac_exp_bar.update_bar()
            else:
                _move_window_to_foreground("Path of Exile")

                pos_in_screen = self.mapToGlobal(QPoint(event.x(), event.y()))

                self._info_board.dismiss()
                self._info_board.set_text_by_template("While Processing")
                self._info_board.show()
                QTimer.singleShot(1, lambda: self._measure(pos_in_screen.x(), pos_in_screen.y()))

                self._menu.setWindowFlags(self._flags_backup)

        elif event.button() == Qt.MouseButton.MiddleButton:
            if self._logic.to_measurer().get_current_entry_page() == 0:
                self._info_board.set_text_by_template("No Entry")
            else:
                self._info_board.set_text_by_template("Result")
            self._info_board.show()
        
        _move_window_to_foreground("Path of Exile")

    def wheelEvent(self, event : QWheelEvent):
        if not self._info_board.is_dismissed():
            self._info_board.dismiss()

        if event.angleDelta().y() > 0:
            self._next_entry()
        else:
            self._previous_entry()

    def showEvent(self, event):
        if not self._info_board.is_dismissed():
            self._info_board.show()

        self._frac_exp_bar.try_show()

    def hideEvent(self, event):
        self._frac_exp_bar.hide()

        if not self._info_board.is_dismissed():
            self._info_board.hide()

        if self._menu.isVisible():
            self._menu.close()

    def enterEvent(self, event: QEnterEvent):
        if self._info_board.is_dismissed():
            self._info_board.show()

    def leaveEvent(self, event: QEvent):
        if self._info_board.is_dismissed():
            self._info_board.hide()

    def _measure(self, cursor_x_in_screen : int, cursor_y_in_screen : int):
        self._foreground_guardian.pause()
        self._logic.measure(cursor_x_in_screen, cursor_y_in_screen, [self])
        self._foreground_guardian.resume()

        if self._logic.is_fetch_failed():
            self._info_board.set_text_by_template("Error")
        else:
            self._info_board.set_text_by_template("Result")

        self._frac_exp_bar.update_bar()

    def _next_entry(self):
        measurer = self._logic.to_measurer()

        measurer.go_to_next_entry()
        page = measurer.get_current_entry_page()
        if page == 0:
            self._info_board.set_text_by_template("On No Entry")
        elif page == measurer.get_number_of_entries():
            self._info_board.set_text_by_template("On Last")
        elif page == 1:
            self._info_board.set_text_by_template("On First")
        else:
            self._info_board.set_text_by_template("On Next")
        self._info_board.show()
        
        self._frac_exp_bar.update_bar()

    def _previous_entry(self):
        measurer = self._logic.to_measurer()

        measurer.go_to_previous_entry()
        page = measurer.get_current_entry_page()
        if page == 0:
            self._info_board.set_text_by_template("On No Entry")
        elif page == 1:
            self._info_board.set_text_by_template("On First")
        elif page == measurer.get_number_of_entries():
            self._info_board.set_text_by_template("On Last")
        else:
            self._info_board.set_text_by_template("On Previous")
        self._info_board.show()
        
        self._frac_exp_bar.update_bar()

    def _dismiss_help(self):
        if self._logic.to_measurer().get_current_entry_page() == 0:
            self._info_board.set_text_by_template("No Entry")
        else:
            self._info_board.set_text_by_template("Result")
        self._info_board.show()

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

        def_format_file_name = data_path + "/formats/Default.format"

        temporal_settings : dict[str, Any] = {
            "data_path" : data_path,
            "def_format_file_name" : def_format_file_name,
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

        if not os.path.exists(def_format_file_name) or is_overwrite_default_format:
            os.makedirs(os.path.dirname(def_format_file_name), exist_ok = True)

            if is_overwrite_default_format and os.path.exists(def_format_file_name):
                os.remove(def_format_file_name)

            source_file_name = os.path.abspath(os.path.dirname(__file__) + "/../assets/Default.format")
            
            shutil.copy(source_file_name, def_format_file_name)

            to_logger().info("Created \"Default.format\".")

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
