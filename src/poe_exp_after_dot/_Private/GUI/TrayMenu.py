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

from ..Commons               import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
from ..Logic                 import Logic, PosData
from ..LogManager            import to_log_manager, to_logger
from ..Settings              import Settings

from .Menu                   import Menu

# path to top level package
_base_path = os.path.abspath(os.path.dirname(__file__) + "/../..")

class TrayMenu(QSystemTrayIcon):
    def __init__(self, menu : Menu):
        # Do not own 'menu'.
        super().__init__()

        icon_file_name =  _base_path + "/assets/icon.png"
        self.setIcon(QIcon(icon_file_name))

        self.setContextMenu(menu)