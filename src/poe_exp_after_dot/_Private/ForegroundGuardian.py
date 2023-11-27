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

from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QWidgetAction, QLineEdit
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent, QLine, QTimer
from PySide6.QtGui      import QColor, QMouseEvent, QIcon, QAction, QCloseEvent, QContextMenuEvent, QFocusEvent, QFont, QEnterEvent, QKeyEvent, QPainter, QWheelEvent, QActionGroup

from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
from .Logic             import Logic, PosData
from .LogManager        import to_log_manager, to_logger
from .Settings          import Settings
from .TextGenerator     import TextGenerator, TemplateLoader
from .CharacterRegister import CharacterRegister, Character

from .GUI.ControlRegionInterface    import ControlRegionInterface

class ForegroundGuardian:
    _control_region : ControlRegionInterface
    _user32         : ctypes.WinDLL
    _is_paused      : bool
    _timer          : QTimer

    def __init__(self, control_region : ControlRegionInterface):
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