from typing import SupportsFloat, SupportsInt

_SECONDS_IN_MINUTE   = 60
_SECONDS_IN_HOUR     = 60 * _SECONDS_IN_MINUTE
_SECONDS_IN_DAY      = 24 * _SECONDS_IN_HOUR
_SECONDS_IN_WEEK     = 7  * _SECONDS_IN_DAY

class FineTime:
    _time                   : float
    _text_representation    : str

    def __init__(self, time_ : SupportsFloat = 0.0, max_unit : str = "w", *, value_color : str | None = None, unit_color : str | None = None):
        """
        time_
            Time in seconds.

        max_unit
            Highest unit in representation form.
            Either: "w", "d", "h", "m", "s".

        value_color
            None or color of all values. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...

        unit_color
            None or color of all unit symbols. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...
        """

        if not isinstance(time_, float):
            self._time = float(time_)
        else:
            self._time = time_

        if max_unit not in ["w", "d", "h", "m", "s"]:
            raise ValueError("Unexpected value of 'max_unit' parameter.")

        weeks,      remain  = divmod(self._time, _SECONDS_IN_WEEK)  if max_unit in ["w"]                else (0, self._time)
        days,       remain  = divmod(remain, _SECONDS_IN_DAY)       if max_unit in ["w", "d"]           else (0, remain)
        hours,      remain  = divmod(remain, _SECONDS_IN_HOUR)      if max_unit in ["w", "d", "h"]      else (0, remain)
        minutes,    seconds = divmod(remain, _SECONDS_IN_MINUTE)    if max_unit in ["w", "d", "h", "m"] else (0, remain)

        is_front = True

        self._text_representation = ""

        vb = f"<font color=\"{value_color}\">" if value_color else ""
        ve = "</font>" if value_color else ""

        b = f"<font color=\"{unit_color}\">" if unit_color else ""
        e = "</font>" if unit_color else ""

        if not is_front or weeks != 0:
            self._text_representation += f"{vb}{weeks:.0f}{ve}{b}w{e}"
            is_front = False

        if not is_front or days != 0:
            self._text_representation += f"{vb}{days:.0f}{ve}{b}d{e}" if is_front else f"{vb}{days:01.0f}{ve}{b}d{e}"
            is_front = False

        if not is_front or hours != 0:
            self._text_representation += f"{vb}{hours:.0f}{ve}{b}h{e}" if is_front else f"{vb}{hours:02.0f}{ve}{b}h{e}"
            is_front = False

        if not is_front or minutes != 0:
            self._text_representation += f"{vb}{minutes:.0f}{ve}{b}m{e}" if is_front else f"{vb}{minutes:02.0f}{ve}{b}m{e}"
            is_front = False
 
        self._text_representation += f"{vb}{seconds:.0f}{ve}{b}s{e}" if is_front else f"{vb}{seconds:02.0f}{ve}{b}s{e}"

    def get_time(self) -> float:
        """
        Returns 
            Time in seconds.
        """
        return self._time

    def __str__(self) -> str:
        return self._text_representation
    
    def __repr__(self) -> str:
        return self._text_representation

class FineExpPerHour:
    _exp_per_hour : int

    def __init__(self, exp_per_hour : SupportsInt = 0, *, value_color : str | None = None, unit_color : str | None = None):
        if not isinstance(exp_per_hour, int):
            self._exp_per_hour = int(exp_per_hour)
        else:
            self._exp_per_hour = exp_per_hour

        exp_per_hour = self._exp_per_hour
        remain = 0
        unit = ""

        if exp_per_hour >= 1000:
            exp_per_hour, remain = divmod(exp_per_hour, 1000)
            unit = "k"

        if exp_per_hour >= 1000:
            exp_per_hour, remain = divmod(exp_per_hour, 1000)
            unit = "m"

        vb = f"<font color=\"{value_color}\">" if value_color else ""
        ve = "</font>" if value_color else ""

        b = f"<font color=\"{unit_color}\">" if unit_color else ""
        e = "</font>" if unit_color else ""

        if exp_per_hour < 10 and unit != "":
            self._text_representation = f"{vb}{exp_per_hour:.0f}.{remain // 10:02}{ve}{b}{unit} exp/h{e}"
        elif exp_per_hour < 100 and unit != "":
            self._text_representation = f"{vb}{exp_per_hour:.0f}.{remain // 100:01}{ve}{b}{unit} exp/h{e}"
        else:
            self._text_representation = f"{vb}{exp_per_hour:.0f}{ve}{b}{unit} exp/h{e}"

    def get_exp_per_hour(self) -> int:
        return self._exp_per_hour

    def __str__(self) -> str:
        return self._text_representation
    
    def __repr__(self) -> str:
        return self._text_representation
