import os as _os

from PySide6.QtWidgets  import QWidget, QMenu, QWidgetAction, QLineEdit
from PySide6.QtCore     import Qt
from PySide6.QtGui      import QMouseEvent, QAction, QActionGroup

from ..Commons          import to_app
from ..Logic            import Logic
from ..LogManager       import to_log_manager, to_logger
from ..OverlaySupport   import solve_layout as _solve_layout
from ..Version          import get_version as _get_version

from .ControlRegionInterface import ControlRegionInterface


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


class FormatMenu(QMenu):
    _logic              : Logic
    _control_region     : ControlRegionInterface

    _action_group       : QActionGroup
    _formats            : dict[str, str] # name, file_name

    def __init__(self, parent : "Menu", logic : Logic, control_region : ControlRegionInterface):
        super().__init__("Format", parent)

        self._logic = logic
        self._control_region = control_region

        self._scan_for_formats()

        current_name = self._logic.to_settings().get_str("info_board_format")

        self._action_group = QActionGroup(self)

        for name in self._formats.keys():
            if name == current_name:
                action = QAction(name, self, checkable = True, checked = True) # type: ignore[call-overload]
                self.setTitle("Format: " + name)
            else:
                action = QAction(name, self, checkable = True, checked = False) # type: ignore[call-overload]
            self.addAction(action)
            action.triggered.connect(self._switch_format)
            self._action_group.addAction(action)

    def _switch_format(self):
        sender : QAction = self.sender() # type: ignore[annotation-unchecked]
        name = sender.text()

        self._control_region.change_info_board_format(name)
        self.setTitle("Format: " + name)
            
    def _scan_for_formats(self):
        data_path = self._logic.to_settings().get_str("_data_path")
        format_folder_path = data_path + "/formats"

        self._formats = {}

        for file_name in _os.listdir(format_folder_path):
            full_file_name = format_folder_path + "/" + file_name
            if _os.path.isfile(full_file_name):
                name, *extension = file_name.split(".", 1)
                if extension and extension[0] == "format":
                    self._formats[name] = full_file_name


class LayoutMenu(QMenu):
    _logic              : Logic
    _control_region     : ControlRegionInterface

    def __init__(self, parent : "Menu", logic : Logic, control_region : ControlRegionInterface):
        super().__init__("Layout", parent)

        self._logic = logic
        self._control_region = control_region

        layouts = logic.to_settings().get_dict("layouts")
        layouts_names = [name for name in layouts.keys()]

        current_layout_name = self._logic.to_settings().get_str("selected_layout_name")

        action = QAction("detect on start", self, checkable = True) # type: ignore[call-overload]
        action.setChecked(self._logic.to_settings().get_bool("is_detect_layout"))
        def set_is_detect_layout(is_enable):
            if is_enable:
                self._logic.to_settings().set_bool("is_detect_layout", True)
            else:
                self._logic.to_settings().set_bool("is_detect_layout", False)
        action.triggered.connect(set_is_detect_layout)
        self.addAction(action)

        self.addSeparator()

        self._action_group = QActionGroup(self)

        for name in layouts_names:
            if name == current_layout_name:
                action = QAction(name, self, checkable = True, checked = True) # type: ignore[call-overload]
                self.setTitle("Layout: " + name)
            else:
                action = QAction(name, self, checkable = True, checked = False) # type: ignore[call-overload]
            self.addAction(action)
            action.triggered.connect(self._switch_layout)
            self._action_group.addAction(action)

    def _switch_layout(self):
        sender : QAction = self.sender() # type: ignore[annotation-unchecked]
        layout_name = sender.text()

        _solve_layout(self._logic.to_settings(), layout_name)
        self._control_region.reposition_and_resize_all()
        self.setTitle("Layout: " + layout_name)

        self._logic.to_settings().set_str("selected_layout_name", layout_name)


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
        sender : QAction = self.sender() # type: ignore[annotation-unchecked]
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
        action : QAction = self.sender() # type: ignore[annotation-unchecked]
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

        version = _get_version()
        self._title = self.addAction(f"poe exp after dot v{version}")
        self._title.setEnabled(False)
        self.addSeparator()

        self.addMenu(ExpDataSubMenu(self, logic, control_region))
        self.addMenu(FormatMenu(self, logic, control_region))
        self.addMenu(LayoutMenu(self, logic, control_region))

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
            _os.startfile(_os.path.abspath(self._logic.to_settings().get_str("_data_path")))
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
        self._enable_debug_action.setChecked(self._logic.to_settings().get_bool("_is_debug"))
        def enable_debug(is_enable):
            if is_enable:
                self._logic.to_settings().set_bool("_is_debug", True)
                to_log_manager().set_is_debug(True)
            else:
                self._logic.to_settings().set_bool("_is_debug", False)
                to_log_manager().set_is_debug(False)

            self._control_region.repaint()

            self.setWindowFlags(self._flags_backup)

        self._enable_debug_action.triggered.connect(enable_debug)
        self.addAction(self._enable_debug_action)

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
