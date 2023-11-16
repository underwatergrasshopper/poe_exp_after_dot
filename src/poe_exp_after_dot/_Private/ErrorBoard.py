import sys as _sys

def run_error_board(x : int, bottom : int | None, message : str, short_message : str) -> int:
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
            self._bottom = bottom
            if self._bottom is None:
                self._bottom = to_app().primaryScreen().size().height() 

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
            self._label.setStyleSheet(f"font: 12px Consolas; color: white;")
            self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 

            self._notice_text_format = (
                "{title_begin}ERROR{title_end}<br>"
                "{hint_begin}"
                "Hold RMB to show Message.<br>"
                "Hold Ctrl + RMB to show Details.<br>"
                "Click to Exit."
                "{hint_end}"
            )

            self._short_message_text_format = (
                "{title_begin}ERROR{title_end}<br>"
                "{short_message}<br>"
                "{hint_begin}"
                "Hold RMB to show Message.<br>"
                "Hold Ctrl + RMB to show Details.<br>"
                "Click to Exit."
                "{hint_end}"
            )

            self._message_text_format = (
                "{title_begin}ERROR{title_end}<br>"
                "{message}<br>"
                "{hint_begin}"
                "Hold RMB to show Message.<br>"
                "Hold Ctrl + RMB to show Details.<br>"
                "Click to Exit."
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
                title_begin     = "<font color=\"#FF0000\">", 
                title_end       = "</font>", 
                short_message   = self._short_message,
                message         = self._message,
                hint_begin      = "<font color=\"#AFAFAF\">",
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
    return to_app().exec_()

if "is_display_error_board" in locals() and locals()["is_display_error_board"]:
    exit_code = run_error_board(
        locals()["x"]               if "x" in locals()              else 0,
        locals()["bottom"]          if "bottom" in locals()         else None,
        locals()["message"]         if "message" in locals()        else "<br>",
        locals()["short_message"]   if "short_message" in locals()  else "<br>"
    )
