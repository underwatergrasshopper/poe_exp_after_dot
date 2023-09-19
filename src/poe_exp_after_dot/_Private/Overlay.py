from typing import SupportsFloat

_SECONDS_IN_MINUTE   = 60
_SECONDS_IN_HOUR     = 60 * _SECONDS_IN_MINUTE
_SECONDS_IN_DAY      = 24 * _SECONDS_IN_HOUR
_SECONDS_IN_WEEK     = 7  * _SECONDS_IN_DAY

class FineTime:
    _time                   : float
    _text_representation    : str

    def __init__(self, time_ : SupportsFloat = 0.0, max_unit : str = "w", *, unit_color : str | None = None):
        """
        time_
            Time in seconds.

        unit_color
            None or color of all unit symbols. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...

        max_unit
            Highest unit in representation form.
            Either: "w", "d", "h", "m", "s".
        """

        if not isinstance(time_, float):
            self._time = float(time_)
        else:
            self._time = time_

        weeks,      remain  = divmod(self._time, _SECONDS_IN_WEEK)  if max_unit in ["w"]                else (0, self._time)
        days,       remain  = divmod(remain, _SECONDS_IN_DAY)       if max_unit in ["w", "d"]           else (0, remain)
        hours,      remain  = divmod(remain, _SECONDS_IN_HOUR)      if max_unit in ["w", "d", "h"]      else (0, remain)
        minutes,    seconds = divmod(remain, _SECONDS_IN_MINUTE)    if max_unit in ["w", "d", "h", "m"]  else (0, remain)

        is_front = True

        self._text_representation = ""

        b = f"<font color=\"{unit_color}\">" if unit_color else ""
        e = "</ font>" if unit_color else ""

        if not is_front or weeks != 0:
            self._text_representation += f"{weeks:.0f}{b}w{e}"
            is_front = False

        if not is_front or days != 0:
            self._text_representation += f"{days:.0f}{b}d{e}" if is_front else f"{days:02.0f}{b}d{e}"
            is_front = False

        if not is_front or hours != 0:
            self._text_representation += f"{hours:.0f}{b}h{e}" if is_front else f"{hours:02.0f}{b}h{e}"
            is_front = False

        if not is_front or minutes != 0:
            self._text_representation += f"{minutes:.0f}{b}m{e}" if is_front else f"{minutes:02.0f}{b}m{e}"
            is_front = False
 
        self._text_representation += f"{seconds:.0f}{b}s{e}" if is_front else f"{seconds:02.0f}{b}s{e}"

    def __str__(self) -> str:
        return self._text_representation
    
    def __repr__(self) -> str:
        return self._text_representation



