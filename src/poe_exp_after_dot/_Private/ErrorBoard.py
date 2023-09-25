
from dataclasses import dataclass

import re

from PySide6.QtCore     import Qt, QPoint, QEvent
from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel
from PySide6.QtGui      import QColor, QMouseEvent, QEnterEvent

class ErrorBoard(QMainWindow):
    @dataclass
    class Share:
        x       : int
        bottom  : int | None

    _share = Share(0, None)

    _screen_width    : int
    _screen_height   : int

    _message        : str
    _short_message  : str

    def __init__(
            self, 
            message         : str, 
            short_message   : str,
            screen_width    : int,
            screen_height   : int
                ):
        super().__init__()

        self._message = message
        self._short_message = short_message

        if self._share.bottom is None:
            _app = QApplication.instance() if QApplication.instance() else QApplication([])
            self._share.bottom = _app.primaryScreen().size().height()

        self._screen_width  = screen_width
        self._screen_height = screen_height

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)
        self.setWindowOpacity(0.7)

        self._label = QLabel("", self)
        self._label.setStyleSheet(f"font: 12px Courier New; font-weight: bold; color: white;")
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) 


        b = ""
        e = ""
        self._place_notice(f"{b}ERROR{e} (Click to quit)<br>Hover to see message.<br>Hold RMB to see details.", is_resize = True)

        b = "<font color=\"#FF0000\">"
        e = "</font>"
        b2 = "<font color=\"#AFAFAF\">"
        e2 = "</font>"
        self._place_notice(f"{b}ERROR{e} (Click to quit)<br>Hover to see message.<br>{b2}Hold RMB to see details.{e2}")

        class ToolTip(QWidget):
            _label  : QLabel

            _x      : int
            _bottom : int
            _max_width : int

            def __init__(self, parent : QWidget, x : int, bottom : int,  screen_width : int):
                super().__init__(parent)

                self._x = x
                self._bottom = bottom
                self._max_width = screen_width - x

                self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
                palette = self.palette()
                palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
                self.setPalette(palette)
                self.setWindowOpacity(0.9)

                self._label = QLabel("", self)
                self._label.setStyleSheet(f"font: 12px Courier New; color: #AFAFAF;")
                self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            def place_message(self, message):
                self._label.setWordWrap(False)  
                self._label.setMaximumWidth(self._max_width)
                self._label.setText(message)
                self._label.adjustSize()
                self.resize(self._label.size())

                self.move( self._x,  self._bottom - self.height())

        self._tooltip = ToolTip(self, self._share.x, self._share.bottom - self._label.height(), screen_width)
        self._tooltip.place_message(short_message)

    def _place_notice(self, notice, *, is_resize = False):
        if is_resize:
            self._label.setWordWrap(False)  
            self._label.setText(notice)

            self._label.adjustSize()
            self.resize(self._label.size())
            self.move(QPoint(self._share.x, self._share.bottom - self._label.height()))
        else:
            self._label.setWordWrap(True)  
            self._label.setText(notice)

    @staticmethod
    def set_default_pos(x : int, bottom : int):
        ErrorBoard._share.x = x
        ErrorBoard._share.bottom = bottom

    def mousePressEvent(self, event: QMouseEvent) -> None:
       if event.button() == Qt.MouseButton.RightButton:
            self._tooltip.place_message(self._message)

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            QApplication.instance().quit()
        elif event.button() == Qt.MouseButton.RightButton:
            self._tooltip.place_message(self._short_message)

    def enterEvent(self, event: QEnterEvent):
        self._tooltip.show()

    def leaveEvent(self, event: QEvent):
        self._tooltip.hide()

def hide_abs_paths(traceback_message : str) -> str:
    lines = traceback_message.split("\n")
    formatted_lines = []
    for line in lines:
        formatted_lines.append(re.sub(r"File \".*([\\/]poe_exp_after_dot.*\.py)\"|File \".*([\\/][^\\/]+\.py)\"", "File \"...\\1\"", line))
    return ("\n".join(formatted_lines)).strip("\n")

def run_error_board(message : str, short_message : str) -> int:
        app = QApplication.instance() if QApplication.instance() else QApplication([])
        app.closeAllWindows()

        screen_size = app.primaryScreen().size()
        exception_board = ErrorBoard(
            message, 
            short_message,
            screen_width    = screen_size.width(),
            screen_height   = screen_size.height()
        )
        exception_board.show()
        return app.exec_()