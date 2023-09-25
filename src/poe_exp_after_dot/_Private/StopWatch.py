from time import time as _get_time

class StopWatch:
    _start          : float     # in seconds
    _stop           : float     # in seconds
    _accumulator    : float     # in seconds
    _elapsed_time   : float     # in seconds

    def __init__(self, *, start : float | None = None):
        """
        start
            Time from the epoch in seconds or None.
        """
        self.reset(start = start)

    def reset(self, *, start : float | None = None):
        """
        start
            Time from the epoch in seconds or None.
        """
        self._start         = _get_time() if start is None else start
        self._stop          = self._start
        self._accumulator   = 0.0
        self._elapsed_time  = 0.0

    def update(self):
        self._stop = _get_time()
        self._accumulator += self._stop - self._start
        self._start = self._stop

        self._elapsed_time, self._accumulator = divmod(self._accumulator, 1.0)

    def get_elapsed_time(self) -> float:
        """
        Returns
            Time in whole seconds.
        """
        return self._elapsed_time
    
    def get_stop_time(self) -> float:
        """
        Returns
            Time from the epoch in seconds.
        """
        return self._stop