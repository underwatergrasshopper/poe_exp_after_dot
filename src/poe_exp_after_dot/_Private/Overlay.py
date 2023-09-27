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
from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, try_get, to_app
from .Logic             import Logic, PosData, CustomPosData
from .LogManager        import to_log_manager, to_logger
from .Settings          import Settings

_HELP_TEXT = """
poe_exp_after_dot.py [<option> ...]

<option>
    --help | -h
        Just displays this information. Application won't run.
    --data-path=<path>
        Relative or absolute path to data folder. 
        In that folder are stored: settings, logs, exp data and other data.
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
        Only not skipped values will override current position data. 

        Example: --custom="10,100;,,,;,,,;,,,"
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

    def __init__(self, logic : Logic, font_name = "Consolas", font_size = 14):
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
        self._label.setStyleSheet(f"font: {font_size}px {font_name}; color: white;")
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
            os.startfile(try_get(self._logic.to_settings(), "data_path", str))
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


class Overlay:
    def __init__(self):
        pass

    def run(self, *, is_debug : bool = False, data_path : str | None = None, custom_pos_data : CustomPosData | None = None) -> int:
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
        to_logger().debug(f"custom_pos_data={custom_pos_data}")

        settings = Settings(data_path + "/settings.json", {
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
        settings.load_and_add_temporal({
            "data_path" : data_path
        })

        to_logger().info("Loaded settings.")

        logic = Logic(settings, custom_pos_data)

        ErrorBoard.set_default_pos(
            x = logic.to_pos_data().click_bar_x,
            bottom = logic.to_pos_data().click_bar_y,
        )

        app = to_app() # initializes global QApplication object

        info_board = InfoBoard(logic)
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
        is_help = False
        data_path : str | None = None
        custom_pos_data : CustomPosData | None = None
        raw_custom_pos_data : str | None = None
        is_debug = False


        for argument in argv[1:]:
            option_name, *value = argument.split("=", 1)

            match (option_name, *value):
                ### correct ###

                case ["--data-path", data_path]:
                    pass

                case ["--debug"]:
                    is_debug = True

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
                        
                        custom_pos_data = CustomPosData(
                            info_board_x                    = next_group(),
                            info_board_bottom               = next_group(),

                            click_bar_x                     = next_group(),
                            click_bar_y                     = next_group(),
                            click_bar_width                 = next_group(),
                            click_bar_height                = next_group(),

                            in_game_exp_bar_x               = next_group(),
                            in_game_exp_bar_y               = next_group(),
                            in_game_exp_bar_width           = next_group(),
                            in_game_exp_bar_height          = next_group(),

                            in_game_exp_tooltip_x_offset    = next_group(),
                            in_game_exp_tooltip_y           = next_group(), 
                            in_game_exp_tooltip_width       = next_group(), 
                            in_game_exp_tooltip_height      = next_group()
                        )
                    else:
                        raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" have wrong format.")
                
                case ["--help" | "-h"]:
                    is_help = True
                
                ### incorrect ###

                case ["--help" | "-h", _]:
                    raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" can't have a value.")
                
                case ["--data-path" | "--custom"]:
                    raise ValueError(f"Incorrect command line argument. Option \"{option_name}\" need to have a value.")

                case [option_name, *_]:
                    raise ValueError(f"Incorrect command line argument. Unknown option \"{option_name}\".")

        if is_help:
            print(_HELP_TEXT)
            return 0
        
        return self.run(
            is_debug = is_debug,
            data_path = data_path,
            custom_pos_data = custom_pos_data,
        )
