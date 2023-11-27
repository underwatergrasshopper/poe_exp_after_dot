import ctypes as _ctypes

from PySide6.QtCore import QTimer

from .GUI.ControlRegionInterface import ControlRegionInterface

class ForegroundGuardian:
    _control_region : ControlRegionInterface
    _user32         : _ctypes.WinDLL
    _is_paused      : bool
    _timer          : QTimer

    def __init__(self, control_region : ControlRegionInterface):
        self._control_region    = control_region
        self._user32            = _ctypes.windll.user32
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