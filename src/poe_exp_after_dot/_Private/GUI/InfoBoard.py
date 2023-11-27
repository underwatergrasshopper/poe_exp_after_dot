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

from ..Commons           import EXIT_FAILURE, EXIT_SUCCESS, to_app, merge_on_all_levels, get_default_data_path
from ..Logic             import Logic, PosData
from ..LogManager        import to_log_manager, to_logger
from ..Settings          import Settings
from ..TextGenerator     import TextGenerator, TemplateLoader
from ..CharacterRegister import CharacterRegister, Character

from .ControlRegionInterface    import ControlRegionInterface


class InfoBoard(QWidget):
    _logic          : Logic
    _control_region : ControlRegionInterface
    _is_dismissed   : bool

    def __init__(self, logic : Logic, control_region : ControlRegionInterface):
        """
        font_size
            In pixels.
        """
        super().__init__()

        self._logic = logic
        self._control_region = control_region
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
        to_logger().info(f"Loading formats for info board from \"{os.path.basename(def_format_file_name)}\" ...")
        template_loader.load_and_parse(logic.to_settings().get_val("def_format_file_name", str))
        to_logger().info("Formats has been loaded.")

        for name, value in template_loader.to_variables().items():
            logic.to_settings().set_val("fmt_var." + name, value, str, is_temporal_only = True)

        self._text_generator = TextGenerator(template_loader.to_templates(), self._logic.get_info_board_text_parameters, self.set_text)
        self._text_generator.start()
        ###

    def set_text_by_template(self, template_name : str | None = None):
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

    def mousePressEvent(self, event: QMouseEvent):
        self._control_region.pause_foreground_guardian()

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide()
            self.dismiss()
            self.set_text_by_template("Just Hint")
        
        self._control_region.resume_foreground_guardian()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(1.0)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 127))