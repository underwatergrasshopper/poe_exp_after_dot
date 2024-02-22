"""
Displays error message on screen.

This module is autonomous from rest of package. 
Should be called separately and only from command line.

ErrorBoard.py --help
    Displays manual.
"""
import sys          as _sys
import os           as _os
import traceback    as _traceback
import re           as _re


_EXIT_SUCCESS = 0
_EXIT_FAILURE = 1

_HELP_TEXT = """
Displays error message on screen.

ErrorBoard.py --help
    Displays manual.

ErrorBoard.py <log_path> <message_file_name> <short_message_file_name> [<option>...]
    Displays error message.
    If fails then error message is logged to "error_board_error_message.txt" in <log_path>.

    <log_path>
        Path to folder where "error_board_error_message.txt" will be create in case of error.
        Each new run will delete this file at start.

    <message_file_name>
        Path to file with full error message, which content will be loaded. 
        Content must be preprocessed to be displayed correctly in PyQt label widget.

    <short_message_file_name>
        Path to file with short error message, which content will be loaded.
        Content must be preprocessed to be displayed correctly in PyQt label widget.

    <option>
        --position="<x>,<y>"
        -p="<x>,<y>"
            Position of error board in screen.

            <x>
                An integer number.
                Default: 0.
            <y>
                An integer number or text 'bottom'.
                If 'bottom', then error board is at the bottom of screen.
                Default: bottom.

            Examples:
                -p="0,bottom"
                -p="100,30"

        --details
            When error occurs, additional option is visible in ErrorBoard, which allows to show details of error.
            Details of error may contain sensitive data.
""".strip("\n")

_ERROR_BOARD_ERROR_MESSAGE_FILE_NAME = "error_board_error_message.txt"


class _ExceptionStash:
    exception : BaseException | None

    def __init__(self):
        self.exception = None

_exception_stash = _ExceptionStash()


class _Error(Exception):
    pass

class _ExecutionError(_Error):
    pass

class _CommandArgumentError(_Error):
    pass


def _run(
        message_file_name       : str, 
        short_message_file_name : str, 
        x                       : int, 
        y                       : int | None,
        *,
        is_details              : bool = False,
            ) -> int:
    import typing

    from PySide6.QtCore     import Qt, QPoint
    from PySide6.QtWidgets  import QMainWindow, QApplication, QLabel
    from PySide6.QtGui      import QColor, QMouseEvent, QPainter, QPaintEvent

    def to_app() -> QApplication:
        app = QApplication.instance()
        if app:
            return typing.cast(QApplication, app)
        return QApplication([])
    
    message_file_name = message_file_name.rstrip("/").rstrip("\\").rstrip("\\")
    if not _os.path.isfile(message_file_name):
        raise _ExecutionError(f"File with error message \"{message_file_name}\" does not exist.")
    
    with open(message_file_name, "r") as file:
        message = file.read()

    short_message_file_name = short_message_file_name.rstrip("/").rstrip("\\").rstrip("\\")
    if not _os.path.isfile(short_message_file_name):
        raise _ExecutionError(f"File with error short message \"{short_message_file_name}\" does not exist.")

    with open(short_message_file_name, "r") as file:
        short_message = file.read()


    class ErrorBoard(QMainWindow):
        _x                      : int
        _y                      : int | None

        _screen_width           : int
        _screen_height          : int

        _message                : str
        _short_message          : str

        _no_enter_leave_check   : bool
        _is_details             : bool

        def __init__(
                self, 
                message         : str, 
                short_message   : str,
                x               : int,
                y               : int | None,
                *,
                is_details      : bool = False
                    ):
            super().__init__()

            self._message       = message
            self._short_message = short_message
            self._is_details    = is_details

            self._x = x
            self._y = y

            self._no_enter_leave_check = False

            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            self._label = QLabel("", self)
            self._label.setStyleSheet(f"font: 12px Consolas; color: #BFBFBF;")
            self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 

            title_section = (
                "{title_begin}FATAL ERROR{title_end}"
            )

            if self._is_details:
                hint_section = (
                    "{hint_begin}"
                    "Left Click on This to Exit.<br>"
                    "Right Click on This to show Message.<br>"
                    "Hold Ctrl + Shift + RMB on This to show Details (may contain sensitive data)."
                    "{hint_end}"
                )
            else:
                hint_section = (
                    "{hint_begin}"
                    "Left Click on This to Exit.<br>"
                    "Right Click on This to show Message."
                    "{hint_end}"
                )
                

            self._notice_text_format = (
                f"{title_section}<br>"
                f"{hint_section}"
            )

            self._short_message_text_format = (
                f"{title_section}<br>"
                "{short_message}<br>"
                f"{hint_section}"
            )

            self._message_text_format = (
                f"{title_section}<br>"
                "{message}<br>"
                f"{hint_section}"
            )

            self._set_text_from_format(self._notice_text_format, is_overexpand_safe = True)

        def _set_text_from_format(self, text_format : str, *, is_overexpand_safe : bool = True):
            if is_overexpand_safe:
                # in case of formatting error, will not overexpand text
                text = self._gen_text(text_format, is_no_formatting = True)
                self._set_text(text, is_resize = True)

                text = self._gen_text(text_format)
                self._set_text(text)
            else:
                text = self._gen_text(text_format)
                self._set_text(text, is_resize = True)

        def _gen_text(self, text_format : str, *, is_no_formatting = False):
            if is_no_formatting:
                return text_format.format(
                    title_begin     = "", 
                    title_end       = "", 
                    short_message   = self._short_message,
                    message         = self._message,
                    hint_begin      = "",
                    hint_end        = "",
                )
            return text_format.format(
                title_begin     = "<font color=\"#DF0000\">", 
                title_end       = "</font>", 
                short_message   = self._short_message,
                message         = self._message,
                hint_begin      = "<font color=\"#7F7F7F\">",
                hint_end        = "</font>",
            )
        
        def _set_text(self, text, *, is_resize = False):
            if is_resize:
                self._label.setWordWrap(False)  
                self._label.setText(text)

                self._label.adjustSize()
                self.resize(self._label.size())
                if self._y is None:
                    screen_height = to_app().primaryScreen().size().height() 
                    y = screen_height - self._label.height()
                else:
                    y = self._y

                self.move(QPoint(self._x, y))
            else:
                self._label.setWordWrap(True)  
                self._label.setText(text)

        def mousePressEvent(self, event: QMouseEvent):
            # raise RuntimeError("Some error inside.") # debug
            if event.button() == Qt.MouseButton.RightButton:
                if to_app().keyboardModifiers() == Qt.KeyboardModifier.NoModifier:
                    self._set_text_from_format(self._short_message_text_format)

                elif self._is_details and to_app().keyboardModifiers() == Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier:
                    self._set_text_from_format(self._message_text_format)


        def mouseReleaseEvent(self, event : QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                to_app().quit()

            elif event.button() == Qt.MouseButton.RightButton:
                self._set_text_from_format(self._notice_text_format)

        def paintEvent(self, event : QPaintEvent):
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 191))

    app = to_app()

    error_board = ErrorBoard(
        message, 
        short_message,
        x,
        y,
        is_details      = is_details
    )
    error_board.show()

    def excepthook(exception_type, exception : BaseException, traceback_type):
        _exception_stash.exception = exception
        # NOTE: With some brief testing, closeEvent was not triggered when exited with _EXIT_FAILURE (or value equal 1). 
        # But for safety, do not implement closeEvent in any widget.
        QApplication.exit(_EXIT_FAILURE)

    previous_excepthook = _sys.excepthook
    _sys.excepthook = excepthook

    exit_code = app.exec()

    _sys.excepthook = previous_excepthook

    if _exception_stash.exception:
        exception = _exception_stash.exception
        _exception_stash.exception = None
        raise exception
    
    return exit_code


def _main_no_error_handling(argv : list[str]) -> int:
    arguments = argv[1:]

    options : list[str] = []
    non_options = []

    for argument in arguments:
        if argument and argument[0] == "-":
            options.append(argument)
        else:
            non_options.append(argument)

    is_run                      = True
    x           : int           = 0
    y           : int | None    = None
    is_details                  = False

    for option in options:
        name, *value = option.split("=", 1)

        match (name, *value):
            case ["--help"]:
                print(_HELP_TEXT)
                is_run = False
            case ["--position" | "-p", position]:
                match_ = _re.search(r"^([^,]*),([^,]*)$", position)
                if match_:
                    try:
                        x = int(match_.group(1))
                    except ValueError:
                        raise _CommandArgumentError("Value 'x' in command line option '--position' must be an integer number.")

                    if match_.group(2) == "bottom":
                        y = None
                    else:
                        try:
                            y = int(match_.group(2))
                        except ValueError:
                            raise _CommandArgumentError("Value 'y' in command line option '--position' must be an integer number.")

            case ["--details"]:
                is_details = True

            case ["--position" | "-p"]:
                raise _CommandArgumentError(f"Command line option \"{name}\" need to have value.")
            case ["--help" | "--details", _]:
                raise _CommandArgumentError(f"Command line option \"{name}\" can not have value.")
            case [name, *_]:
                raise _CommandArgumentError(f"Command line option \"{name}\" is unknown.")
        
    if is_run:
        try:
            log_path = non_options.pop(0)
        except IndexError:
            _CommandArgumentError("Command line arguments missing <log_path>.")

        try:
            message_file_name = non_options.pop(0)
        except IndexError:
            _CommandArgumentError("Command line arguments missing <message_file_name>.")

        try:
            short_message_file_name = non_options.pop(0)
        except IndexError:
            _CommandArgumentError("Command line arguments missing <short_message_file_name>.")

        _remove_error_board_error_message_file(log_path)

        return _run(message_file_name, short_message_file_name, x, y, is_details = is_details)

    return _EXIT_SUCCESS


def _remove_error_board_error_message_file(log_path : str):
    file_name = log_path + "\\" + _ERROR_BOARD_ERROR_MESSAGE_FILE_NAME
    if _os.path.isfile(file_name):
        _os.remove(file_name)


def _main(argv : list[str]) -> int:
    try:
       return _main_no_error_handling(argv)
    except Exception as error:
        if len(argv) > 1:
            log_path = argv[1]
            _os.makedirs(log_path, exist_ok = True)

            file_name = log_path + "\\" + _ERROR_BOARD_ERROR_MESSAGE_FILE_NAME

            with open(file_name, "w") as file:
                if isinstance(error, _Error):
                    file.write(str(error))
                else:
                    file.write(_traceback.format_exc())

            print(f"Exception occurred. Exception message is logged to \"{file_name}\".")
        else:
            if not isinstance(error, _Error):
                raise

            print(error, flush = True)

    return _EXIT_FAILURE


if __name__ == "__main__":
    _sys.exit(_main(_sys.argv))
