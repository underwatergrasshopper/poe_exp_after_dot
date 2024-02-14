import os as _os

from PySide6.QtWidgets  import QSystemTrayIcon, QMenu
from PySide6.QtGui      import QIcon

from .Menu import Menu

# path to top level package
_base_path = _os.path.abspath(_os.path.dirname(__file__) + "\\..\\..")

class TrayMenu(QSystemTrayIcon):
    def __init__(self, menu : Menu):
        # Do not own 'menu'.
        super().__init__()

        icon_file_name =  _base_path + "\\assets\\icon.png"
        self.setIcon(QIcon(icon_file_name))

        self.setContextMenu(menu)