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

def _align_to_bottom(menu : QMenu, bottom : int | None = None):
    rect = menu.geometry()
    if bottom is None:
        bottom = to_app().primaryScreen().size().height()
    current_bottom = rect.bottom()
    if current_bottom != bottom:
        rect.setY(bottom - rect.height())
        menu.setGeometry(rect)
        menu.adjustSize()


NONE_NAME = "[None]"

class CharacterData:
    _name                   : str
    _data_path              : str

    _character_folder_path  : str | None
    _exp_data_file_name     : str

    def __init__(self, name : str, data_path : str):
        """
        name 
            Name of character or NONE_NAME.
        """
        self._name                  = name
        self._data_path             = data_path

        if name != NONE_NAME:
            self._character_folder_path     = os.path.abspath(data_path) + "/characters/" + name
            self._exp_data_file_name        = self._character_folder_path + "/exp_data.json"
        else:
            self._character_folder_path     = None
            self._exp_data_file_name        = os.path.abspath(data_path) + "/exp_data.json"

        self._create()

    def get_name(self) -> str:
        return self._name
    
    def get_exp_data_file_name(self) -> str:
        return self._exp_data_file_name

    def _create(self):
        if self._character_folder_path is not None:
            os.makedirs(self._character_folder_path, exist_ok = True)

        if not os.path.exists(self._exp_data_file_name):
            with open(self._exp_data_file_name, "w") as file:
                file.write("[]")

    def destroy(self):
        if os.path.isfile(self._exp_data_file_name):
            os.remove(self._exp_data_file_name)

        # to make sure it's a correct folder
        if self._character_folder_path is not None and "characters" in self._character_folder_path and len(os.listdir(self._character_folder_path)) == 0:
            os.rmdir(self._character_folder_path)

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

    _characters         : dict[str, CharacterData]

    _separator          : QAction
    _line_edit          : QLineEdit
    _remove_menu        : PersistentMenu
    _remove_menu_separator : QAction

    def __init__(self, parent : "Menu", logic : Logic, control_region : ControlRegionInterface):
        super().__init__("Character", parent)

        self._logic = logic
        self._control_region = control_region

        data_path = self._get_data_path()

        selected = logic.to_settings().get_val("character_name", str)
        if selected == "":
            selected = NONE_NAME

        self._characters = {NONE_NAME : CharacterData(NONE_NAME, data_path)} | self._fetch_characters()

        for character_name in self._characters.keys():
            if selected == character_name:
                self.setTitle("Character: " + character_name)

            action = QAction(character_name, self)
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
        for name in self._characters.keys():
            if name != NONE_NAME:
                action = self._remove_menu.addAction(name)
                action.triggered.connect(self._remove_character)
                self._remove_menu.register_no_close_action(action)

        self._remove_menu_separator = self._remove_menu.addSeparator()  

        action = QAction("All", self)
        action.triggered.connect(self._remove_all_characters)
        self._remove_menu.addAction(action)
        self._remove_menu.register_no_close_action(action)
    
    def _add_character(self):
        name = self._line_edit.text()
        self._line_edit.setText("")

        if name not in ["", "Add", "Remove", "All", NONE_NAME]:
            action = QAction(name, self)
            action.triggered.connect(self._switch_character)
            self.insertAction(self._separator, action)
            _align_to_bottom(self)

            action = QAction(name, self._remove_menu)
            action.triggered.connect(self._remove_character)
            self._remove_menu.insertAction(self._remove_menu_separator, action)
            self._remove_menu.register_no_close_action(action)
            _align_to_bottom(self._remove_menu)
   
            self._characters[name] = CharacterData(name, self._get_data_path())

        self._line_edit.setFocus()

    def _remove_all_characters(self):
        names = [name for name in self._characters.keys()]
        for name in names:
            if name != NONE_NAME:
                self._remove_character_by_name(name)

    def _remove_character(self):
        sender : QAction = self.sender()
        name = sender.text()
        self._remove_character_by_name(name, sender)

    def _remove_character_by_name(self, name : str, remove_menu_action : QAction | None = None):
        if remove_menu_action is None:
            for action in self._remove_menu.actions():
                if action.text() == name:
                    remove_menu_action = action

        if name in self._characters.keys():
            def find_action() -> QAction | None:
                for action in self.actions():
                    if action.text() == name:
                        return action
                return None
            action = find_action()

            if action is not None:
                self.removeAction(action)
                _align_to_bottom(self)
            
                if remove_menu_action is not None:
                    self._remove_menu.removeAction(remove_menu_action)
                    _align_to_bottom(self._remove_menu)

                if self._logic.to_settings().get_val("character_name", str) == name:
                    self._switch_character(character_name = NONE_NAME)

                self._characters[name].destroy()
                del self._characters[name]

    def _switch_character(self, *, character_name : str | None = None):
        if character_name is None:
            action : QAction = self.sender()
            character_name = action.text()

        self.setTitle("Character: " + character_name)

        file_name = self._characters[character_name].get_exp_data_file_name()
        self._logic.to_measurer().switch_exp_data(file_name)
        self._control_region.refresh()

        self._logic.to_settings().set_val("character_name", character_name if character_name != NONE_NAME else "", str)

    def _fetch_characters(self) -> dict[str, CharacterData]:
        characters = {}

        characters_path = self._get_data_path() + "/characters"

        if os.path.exists(characters_path):
            for name in os.listdir(characters_path):
                characters[name] = CharacterData(name, self._get_data_path())

        return characters
    
    def _get_data_path(self) -> str:
        return os.path.abspath(self._logic.to_settings().get_val("data_path", str))

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