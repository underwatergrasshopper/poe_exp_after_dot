import os

from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass

from PySide6.QtWidgets  import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QWidgetAction, QLineEdit
from PySide6.QtCore     import Qt, QPoint, QRect, QEvent, QLine, QTimer
from PySide6.QtGui      import QColor, QMouseEvent, QIcon, QAction

from .ControlRegionInterface import ControlRegionInterface

from ..Commons           import EXIT_FAILURE, EXIT_SUCCESS, to_app
from ..Logic             import Logic, PosData
from ..LogManager        import to_log_manager, to_logger
from ..Settings          import Settings
from ..CharacterRegister import CharacterRegister, Character


GENERIC_CHARACTER_NAME = "[None]"


def _to_description_name(character_name : str) -> str:
    """
    Returns
        Name which should be used in QWidget text, title, description.
    """
    if character_name == "":
        return GENERIC_CHARACTER_NAME
    return character_name


def _to_character_name(description_name : str) -> str:
    if description_name == GENERIC_CHARACTER_NAME:
        return ""
    return description_name


def _align_to_bottom(menu : QMenu, bottom : int | None = None):
    rect = menu.geometry()
    if bottom is None:
        bottom = to_app().primaryScreen().size().height()
    current_bottom = rect.bottom()
    if current_bottom != bottom:
        rect.setY(bottom - rect.height())
        menu.setGeometry(rect)
        menu.adjustSize()


def _find_action(menu : QMenu, text : str) -> QAction | None:
    for action in menu.actions():
        if action.text() == text:
            return action
    return None


class PersistentMenu(QMenu):
    _no_close_actions : list[QAction]

    def __init__(self, title : str, parent : QWidget):
        super().__init__(title, parent)

        self.setMouseTracking(True)

        self._no_close_actions = []

    def register_no_close_action(self, action):
        self._no_close_actions.append(action)

    def mouseReleaseEvent(self, event : QMouseEvent):
        action = self.activeAction()
        if action and action.isEnabled() and action in self._no_close_actions:
            action.setEnabled(False)
            super().mouseReleaseEvent(event)
            action.setEnabled(True)
            action.trigger()
        else:
            super().mouseReleaseEvent(event)


class ExpDataSubMenu(PersistentMenu):
    _logic              : Logic
    _control_region     : ControlRegionInterface

    _separator          : QAction
    _line_edit          : QLineEdit
    _remove_menu        : PersistentMenu
    _remove_menu_separator : QAction

    def __init__(self, parent : "Menu", logic : Logic, control_region : ControlRegionInterface):
        super().__init__("Character", parent)

        self._logic = logic
        self._control_region = control_region

        for character_name in self._logic.to_character_register().get_character_names(is_include_empty_name = True):
            if character_name == logic.get_character_name():
                self.setTitle("Character: " + _to_description_name(character_name))

            action = QAction(_to_description_name(character_name), self)
            action.triggered.connect(self._switch_character)
            self.addAction(action)

        self._separator = self.addSeparator()

        action = QWidgetAction(self)
        self._line_edit = QLineEdit(self)
        self._line_edit.returnPressed.connect(self._add_character)
        action.setDefaultWidget(self._line_edit)
        self.addAction(action)
        self.register_no_close_action(action)

        action = QAction("Add", self)
        action.triggered.connect(self._add_character)
        self.addAction(action)
        self.register_no_close_action(action)

        self.addSeparator()

        self._remove_menu = PersistentMenu("Remove", self)
        self.addMenu(self._remove_menu)
        for character_name in self._logic.to_character_register().get_character_names(is_include_empty_name = False):
            action = self._remove_menu.addAction(_to_description_name(character_name))
            action.triggered.connect(self._remove_character)
            self._remove_menu.register_no_close_action(action)

        self._remove_menu_separator = self._remove_menu.addSeparator()  

        action = QAction("All", self)
        action.triggered.connect(self._remove_all_characters)
        self._remove_menu.addAction(action)
        self._remove_menu.register_no_close_action(action)
    
    def _add_character(self):
        description_name = self._line_edit.text()
        self._line_edit.setText("")

        if description_name not in ["", "Add", "Remove", "All", GENERIC_CHARACTER_NAME]:
            action = QAction(description_name, self)
            action.triggered.connect(self._switch_character)
            self.insertAction(self._separator, action)
            _align_to_bottom(self)

            action = QAction(description_name, self._remove_menu)
            action.triggered.connect(self._remove_character)
            self._remove_menu.insertAction(self._remove_menu_separator, action)
            self._remove_menu.register_no_close_action(action)
            _align_to_bottom(self._remove_menu)
   
            self._logic.to_character_register().add_character(_to_character_name(description_name))

        self._line_edit.setFocus()

    def _remove_all_characters(self):
        for character_name in self._logic.to_character_register().get_character_names(is_include_empty_name = False):
            self._remove_character_by_character_name(character_name)

    def _remove_character(self):
        sender : QAction = self.sender()
        description_name = sender.text()
        self._remove_character_by_character_name(_to_character_name(description_name), sender)

    def _remove_character_by_character_name(self, character_name : str, remove_menu_action : QAction | None = None):
        description_name = _to_description_name(character_name)

        if remove_menu_action is None:
            remove_menu_action = _find_action(self._remove_menu, description_name)

        if character_name in self._logic.to_character_register().get_character_names(is_include_empty_name = False):
            action = _find_action(self, description_name)

            if action is not None:
                self.removeAction(action)
                _align_to_bottom(self)
            
                if remove_menu_action is not None:
                    self._remove_menu.removeAction(remove_menu_action)
                    _align_to_bottom(self._remove_menu)

                if character_name == self._logic.get_character_name():
                    self._switch_character_by_character_name("")

                self._logic.to_character_register().destroy_character(character_name)

    def _switch_character(self):
        action : QAction = self.sender()
        character_name = _to_character_name(action.text())
        self._switch_character_by_character_name(character_name)

    def _switch_character_by_character_name(self, character_name : str):
        self.setTitle("Character: " + _to_description_name(character_name))

        self._logic.switch_character(character_name)
        self._control_region.refresh()


class Menu(QMenu):
    _logic                      : Logic
    _control_region             : ControlRegionInterface 

    _clear_log_file_action      : QAction
    _open_data_folder_action    : QAction
    _hide_action                : QAction
    _enable_debug_action        : QAction
    _quit_action                : QAction
    _close_menu_action          : QAction

    _title                      : QAction
    _flags_backup               : Qt.WindowType

    def __init__(self, logic : Logic, control_region : ControlRegionInterface):
        super().__init__()

        self._logic = logic
        self._control_region = control_region

        self._title = self.addAction("poe exp after dot")
        self._title.setEnabled(False)
        self.addSeparator()

        self._flags_backup = self.windowFlags()
        
        self._clear_log_file_action = QAction("Clear Log File", self)
        def clear_log_file():
            to_log_manager().clear_log_file()
            to_logger().info("Cleared runtime.log.")
            self.setWindowFlags(self._flags_backup)         

        self._clear_log_file_action.triggered.connect(clear_log_file)
        self.addAction(self._clear_log_file_action)

        self._open_data_folder_action = QAction("Open Data Folder", self)
        def open_data_folder():
            os.startfile(os.path.abspath(self._logic.to_settings().get_val("data_path", str)))
            self.setWindowFlags(self._flags_backup)

        self._open_data_folder_action.triggered.connect(open_data_folder)
        self.addAction(self._open_data_folder_action)

        self._hide_action = QAction("Hide Overlay", self, checkable = True) # type: ignore
        def hide_overlay(is_hide):
            if is_hide:
                self._control_region.pause_foreground_guardian_and_hide()
            else:
                self._control_region.resume_foreground_guardian()
            self.setWindowFlags(self._flags_backup)

        self._hide_action.triggered.connect(hide_overlay)
        self.addAction(self._hide_action)

        self._enable_debug_action = QAction("Enable Debug", self, checkable = True) # type: ignore
        self._enable_debug_action.setChecked(self._logic.to_settings().get_val("is_debug", bool))
        def enable_debug(is_enable):
            if is_enable:
                self._logic.to_settings().set_val("is_debug", True, bool)
                to_log_manager().set_is_debug(True)
            else:
                self._logic.to_settings().set_val("is_debug", False, bool)
                to_log_manager().set_is_debug(False)

            self._control_region.repaint()

            self.setWindowFlags(self._flags_backup)

        self._enable_debug_action.triggered.connect(enable_debug)
        self.addAction(self._enable_debug_action)

        self.addMenu(ExpDataSubMenu(self, logic, control_region))

        self.addSeparator()

        self._close_menu_action = QAction("Close Menu", self)
        self._close_menu_action.triggered.connect(self.close)
        self.addAction(self._close_menu_action)

        self._quit_action = QAction("Quit", self)
        def quit():
            to_logger().info("Quitting...")
            to_app().quit()
        self._quit_action.triggered.connect(quit)

        self.addAction(self._quit_action)
