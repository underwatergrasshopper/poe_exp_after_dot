"""
Displays error message.

Should be called separately from package and only from command line.

Semantic:
    ErrorBoard.py <error_board_exception_file_name> <message_file_name> <short_message_file_name> [<x> [<bottom>]]

    <error_board_exception_file_name> 
        File to which error board's exception message will be logged.

    <message>
        Path to file with exception message which must be preprocessed to be displayed correctly in PyQt label widget.

    <short_message>
        Path to file with exception short message which must be preprocessed to be displayed correctly in PyQt label widget.

    <x>
        Position of board's left edge on X axis in screen. Default is 0.

    <bottom>
        Position of board's bottom edge on Y axis in screen. Default is screen's height.
"""
import sys          as _sys
import os           as _os
import traceback    as _traceback


class _ExceptionStash:
    exception : BaseException | None

    def __init__(self):
        self.exception = None

_exception_stash = _ExceptionStash()


def _run(
        message         : str, 
        short_message   : str, 
        x               : int, 
        bottom          : int | None
            ) -> int:
    import typing

    from PySide6.QtCore     import Qt, QPoint, QEvent, QTimer
    from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel
    from PySide6.QtGui      import QColor, QMouseEvent, QEnterEvent, QPainter, QKeyEvent, QPaintEvent

    def to_app() -> QApplication:
        app = QApplication.instance()
        if app:
            return typing.cast(QApplication, app)
        return QApplication([])

    class ErrorBoard(QMainWindow):
        _x                      : int
        _bottom                 : int

        _screen_width           : int
        _screen_height          : int

        _message                : str
        _short_message          : str

        _no_enter_leave_check   : bool

        def __init__(
                self, 
                message         : str, 
                short_message   : str,
                x               : int,
                bottom          : int | None,
                screen_width    : int,
                screen_height   : int
                    ):
            super().__init__()

            self._message       = message
            self._short_message = short_message

            self._x = x
            
            if bottom is None:
                self._bottom = to_app().primaryScreen().size().height() 
            else:
                self._bottom = bottom

            self._screen_width  = screen_width
            self._screen_height = screen_height

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

            self._notice_text_format = (
                "{title_begin}FATAL ERROR{title_end}<br>"
                "{hint_begin}"
                "Hold RMB on This to show Message.<br>"
                "Hold Ctrl + RMB on This to show Details.<br>"
                "Click on This to Exit."
                "{hint_end}"
            )

            self._short_message_text_format = (
                "{title_begin}FATAL ERROR{title_end}<br>"
                "{short_message}<br>"
                "{hint_begin}"
                "Hold RMB on This to show Message.<br>"
                "Hold Ctrl + RMB on This to show Details.<br>"
                "Click on This to Exit."
                "{hint_end}"
            )

            self._message_text_format = (
                "{title_begin}FATAL ERROR{title_end}<br>"
                "{message}<br>"
                "{hint_begin}"
                "Hold RMB on This to show Message.<br>"
                "Hold Ctrl + RMB on This to show Details.<br>"
                "Click on This to Exit."
                "{hint_end}"
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
                self.move(QPoint(self._x, self._bottom - self._label.height()))
            else:
                self._label.setWordWrap(True)  
                self._label.setText(text)

        def mousePressEvent(self, event: QMouseEvent):
            # raise RuntimeError("Some error inside.") # debug
            if event.button() == Qt.MouseButton.RightButton:
                if to_app().keyboardModifiers() & Qt.KeyboardModifier.ControlModifier:
                    self._set_text_from_format(self._message_text_format)
                else:
                    self._set_text_from_format(self._short_message_text_format)

        def mouseReleaseEvent(self, event : QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                to_app().quit()
            elif event.button() == Qt.MouseButton.RightButton:
                self._set_text_from_format(self._notice_text_format)

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key.Key_Control:
                if to_app().mouseButtons() & Qt.MouseButton.RightButton:
                    self._set_text_from_format(self._message_text_format)

        def keyReleaseEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key.Key_Control:
                if to_app().mouseButtons() & Qt.MouseButton.RightButton:
                    self._set_text_from_format(self._short_message_text_format)

        def paintEvent(self, event : QPaintEvent):
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 191))


    screen_size = to_app().primaryScreen().size()
    exception_board = ErrorBoard(
        message, 
        short_message,
        x,
        bottom,
        screen_width    = screen_size.width(),
        screen_height   = screen_size.height()
    )
    exception_board.show()

    EXIT_FAILURE = 1

    def excepthook(exception_type, exception : BaseException, traceback_type):
        _exception_stash.exception = exception
        # NOTE: With some brief testing, closeEvent was not triggered when exited with _EXIT_FAILURE (or value equal 1). 
        # But for safety, do not implement closeEvent in any widget.
        QApplication.exit(EXIT_FAILURE)

    previous_excepthook = _sys.excepthook
    _sys.excepthook = excepthook

    exit_code = to_app().exec()

    _sys.excepthook = previous_excepthook

    if _exception_stash.exception:
        exception = _exception_stash.exception
        _exception_stash.exception = None
        raise exception
    
    return exit_code


def _main(argv : list[str]) -> int:
    if len(argv) <= 3:
        raise ValueError("Not enough arguments were given through command line. At lest 3 argument is expected.")
    
    message_file_name = argv[2]
    message_file_name = message_file_name.rstrip("/").rstrip("\\").rstrip("\\")
    if not _os.path.isfile(message_file_name):
        raise RuntimeError("File with error message does not exist.")
    
    with open(message_file_name, "r") as file:
        message = file.read()

    short_message_file_name = argv[3]
    short_message_file_name = short_message_file_name.rstrip("/").rstrip("\\").rstrip("\\")
    if not _os.path.isfile(short_message_file_name):
        raise RuntimeError("File with error short message does not exist.")

    with open(short_message_file_name, "r") as file:
        short_message = file.read()

    if len(argv) > 4:
        x_text = argv[4]
        if x_text.lstrip("-").isdigit():
            x = int(x_text)
        else:
            raise TypeError("Fifth argument is not an integer.")
    else:
        x = 0

    # raise RuntimeError("Some error inside.") # debug

    if len(argv) > 5:
        bottom_text = argv[5]
        if bottom_text.lstrip("-").isdigit():
            bottom = int(bottom_text)
        else:
            raise TypeError("Sixth argument is not an integer.")
    else:
        bottom = None

    return _run(message, short_message, x, bottom)


if __name__ == "__main__":
    try:
        _sys.exit(_main(_sys.argv))
    except Exception as _exception:
        if len(_sys.argv) > 1:
            _exception_file_name = _sys.argv[1]

            if "error_board_exception_message.txt" in _exception_file_name:
                with open(_exception_file_name, "w") as _file:
                    _file.write(_traceback.format_exc())

        raise RuntimeError("Exception ocurred inside ErrorBoard. Exception message should be already logged to error_board_exception_message.txt in data folder.") from _exception