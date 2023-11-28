import ctypes as _ctypes

from PySide6.QtWidgets  import QMainWindow
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent, QTimer
from PySide6.QtGui      import QColor, QMouseEvent, QEnterEvent, QPainter, QWheelEvent

from ..Commons               import to_app
from ..Logic                 import Logic
from ..ForegroundGuardian    import ForegroundGuardian

from .ControlRegionInterface    import ControlRegionInterface
from .Menu                      import Menu
from .InfoBoard                 import InfoBoard
from .FracExpBar                import FracExpBar


_NOTHING = 0
_CTRL    = Qt.KeyboardModifier.ControlModifier
_SHIFT   = Qt.KeyboardModifier.ShiftModifier
_ALT     = Qt.KeyboardModifier.AltModifier


def _get_key_modifiers():
    mask = _CTRL | _SHIFT | _ALT
    return to_app().keyboardModifiers() & mask


def _move_window_to_foreground(window_name : str):
    user32 = _ctypes.windll.user32

    window_handle = user32.FindWindowW(None, window_name)
    if window_handle:
        user32.SetForegroundWindow(window_handle)


class ControlRegion(QMainWindow, ControlRegionInterface):
    _logic                  : Logic         # reference
    _info_board             : InfoBoard
    _frac_exp_bar           : FracExpBar
    _menu                   : Menu

    _flags_backup           : Qt.WindowType
    _foreground_guardian    : ForegroundGuardian

    def __init__(self, logic : Logic):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setGeometry(QRect(
            logic.to_settings().get_val("_solved_pos_data.control_region_x", int),
            logic.to_settings().get_val("_solved_pos_data.control_region_y", int),
            logic.to_settings().get_val("_solved_pos_data.control_region_width", int),
            logic.to_settings().get_val("_solved_pos_data.control_region_height", int),
        ))

        self._logic         = logic

        self._info_board    = InfoBoard(logic, self)
        self._frac_exp_bar  = FracExpBar(logic)
        self._menu          = Menu(logic, self)

        self._flags_backup = self._menu.windowFlags()
        
        self._foreground_guardian = ForegroundGuardian(self)
                
        if logic.to_measurer().get_number_of_entries() > 0:
            self._info_board.dismiss()
            self._info_board.set_text_by_template("Result")
            self._frac_exp_bar.update_bar(is_try_show = False)
        else:
            self._info_board.set_text_by_template("First Help")
        
    def to_menu(self) -> Menu:
        return self._menu
 
    def refresh(self):
        self._info_board.dismiss()
        if self._logic.to_measurer().get_number_of_entries() > 0:
            self._info_board.set_text_by_template("Result")
        else:
            self._info_board.set_text_by_template("No Entry")
        self._frac_exp_bar.update_bar()

    def start_foreground_guardian(self):
        self._foreground_guardian.start()

    def pause_foreground_guardian_and_hide(self):
        self._foreground_guardian.pause()
        self.hide()

    def pause_foreground_guardian(self):
        self._foreground_guardian.pause()

    def resume_foreground_guardian(self):
        self._foreground_guardian.resume()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

        if self._logic.to_settings().get_val("_is_debug", bool):
            painter.setPen(QColor(0, 255, 0))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
    def mousePressEvent(self, event : QMouseEvent):
        # raise RuntimeError("Some error.") # debug

        if self._menu.isVisible():
            self._menu.close()

        if not self._info_board.is_dismissed():
            self._info_board.dismiss()

        _move_window_to_foreground("Path of Exile")

        modifiers = _get_key_modifiers()

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
                # NOTE: Can't hide menu on PoE losing foreground, 
                # because clicking on menu element is also counted as PoE losing foreground, 
                # and action won't be executed.

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
            elif modifiers == (_CTRL | _SHIFT | _ALT):
                self._logic.to_measurer().remove_current_entry_and_all_entries_above()
                self.refresh()
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