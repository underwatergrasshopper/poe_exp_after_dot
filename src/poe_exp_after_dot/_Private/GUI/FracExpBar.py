from PySide6.QtWidgets  import QWidget
from PySide6.QtCore     import Qt, QRect
from PySide6.QtGui      import QColor, QPainter

from ..Logic             import Logic


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

        self.reposition_and_resize()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.update_bar_manually(0.0, 0.0, is_try_show = False)

    def reposition_and_resize(self):
        self.setGeometry(QRect(
            self._logic.to_settings().get_int("_solved_layout.in_game_exp_bar_x"),
            self._logic.to_settings().get_int("_solved_layout.in_game_exp_bar_y"),
            self._logic.to_settings().get_int("_solved_layout.in_game_exp_bar_width"),
            self._logic.to_settings().get_int("_solved_layout.in_game_exp_bar_height"),
        ))

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
            base_width = frac_progress_base
            step_width = progress_step
        else:
            base_width = 0.0
            step_width = gain % 1

        width = self._logic.to_settings().get_int("_solved_layout.in_game_exp_bar_width")
        self._base_width = int((base_width * width) // 1)
        self._step_width = int((step_width * width) // 1)

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