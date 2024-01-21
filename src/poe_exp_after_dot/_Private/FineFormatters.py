from typing import SupportsFloat, SupportsInt

SECONDS_IN_MINUTE   = 60
SECONDS_IN_HOUR     = 60 * SECONDS_IN_MINUTE
SECONDS_IN_DAY      = 24 * SECONDS_IN_HOUR
SECONDS_IN_WEEK     = 7  * SECONDS_IN_DAY

LT = "&lt;"
GT = "&gt;"

class FineExp:
    MAX_LENGTH_AFTER_FORMAT : int   = 17
    # format for out of range
    # >4'250'334'444exp
    #             <0exp

    _exp                    : int
    _text_representation    : str

    def __init__(self, exp : SupportsInt = 0, *, value_color : str | None = None, unit_color : str | None = None):
        """
        value_color
            None or color of all values. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...
        unit_color
            None or color of all values. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...
        """
        if not isinstance(exp, int):
            self._exp = int(exp)
        else:
            self._exp = exp

        vb = f"<font color=\"{value_color}\">" if value_color else ""
        ve = "</font>" if value_color else ""

        b = f"<font color=\"{unit_color}\">" if unit_color else ""
        e = "</font>" if unit_color else ""

        if self._exp > 4250334444:
            exp = 4250334444
            prefix = GT
        elif self._exp < 0:
            exp = 0
            prefix = LT
        else:
            exp = self._exp
            prefix = ""
        
        exp, remain = divmod(exp, 1000)
        if exp > 0:
            exp_text = f"{remain:03}"
        else:
            exp_text = f"{remain}"

        while exp > 0:
            exp, remain = divmod(exp, 1000)
            if exp > 0:
                exp_text = f"{remain:03}{b}'{e}" + exp_text
            else:
                exp_text = f"{remain}{b}'{e}" + exp_text

        self._text_representation = f"{prefix}{vb}{exp_text}{ve}{b}exp{e}"

    def get_exp(self) -> int:
        return self._exp
    
    def __str__(self) -> str:
        return self._text_representation


class FineBareLevel:
    MAX_LENGTH_AFTER_FORMAT : int   = 4
    # format for out of range:
    # >100
    #   <0

    _level                  : int
    _text_representation    : str

    def __init__(self, level : SupportsInt = 0, *, value_color : str | None = None):
        """
        value_color
            None or color of all values. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...
        """
        if not isinstance(level, int):
            self._level = int(level)
        else:
            self._level = level

        if self._level < 0:
            self._text_representation = f"{LT}0"
        elif self._level > 100:
            self._text_representation = f"{GT}100"
        else:
            self._text_representation = str(self._level)

    def get_level(self) -> int:
        return self._level

    def __str__(self) -> str:
        return self._text_representation


class FineTime:
    MAX_LENGTH_AFTER_FORMAT  : int   = 15

    # format:
    # XXwXdXXhXXmXXs (milliseconds are cut off)
    #         0sXXms (fractional part of millisecond is cut off)
    # XXXXXXXXXXXXXw (days are cut off)

    # format for out of range:
    # >9999999999999w
    # >99w6d23h59m59s
    # >9999d23h59m59s
    # >9999999h59m59s
    # >9999999999m59s
    # >9999999999999s
    #             <0s

    # format for below measurement:
    #             <1s
    #            <1ms

    _time                   : float
    _text_representation    : str

    def __init__(
            self, 
            time_                   : SupportsFloat = 0.0, 
            max_unit                : str           = "w", 
            *, 
            value_color             : str | None    = None, 
            unit_color              : str | None    = None, 
            never_color             : str | None    = None,
            is_just_weeks_if_cap    : bool          = True,
            is_show_ms_if_below_1s  : bool          = False
                ):
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

        never_color
            None or color of all unit symbols. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...

        is_just_weeks_if_cup
            If true and number of weeks is higher than 99, then only weeks are represented on max number of digit equal 14.
        """

        if not isinstance(time_, float):
            self._time = float(time_)
        else:
            self._time = time_

        if max_unit not in ["w", "d", "h", "m", "s"]:
            raise ValueError("Unexpected value of 'max_unit' parameter.")

        vb = f"<font color=\"{value_color}\">" if value_color else ""
        ve = "</font>" if value_color else ""

        b = f"<font color=\"{unit_color}\">" if unit_color else ""
        e = "</font>" if unit_color else ""

        if self._time == float('inf'):
            nb = f"<font color=\"{never_color}\">" if never_color else ""
            ne = "</font>" if never_color else ""

            self._text_representation = f"{nb}never{ne}"

        elif self._time < 0.0:
            self._text_representation = f"{LT}{vb}0{ve}{b}s{e}" 

        elif self._time == 0.0:
            self._text_representation = f"{vb}0{ve}{b}s{e}" 

        elif self._time < 1.0:
            if is_show_ms_if_below_1s:
                milliseconds = self._time * 100
                milliseconds, remain = divmod(milliseconds, 1.0) # rounding prevention

                if milliseconds == 0.0:
                    self._text_representation = f"{LT}{vb}1{ve}{b}ms{e}" 
                else:
                    self._text_representation = f"{vb}0{ve}{b}s{e}" 
                    self._text_representation += f"{vb}{milliseconds:02.0f}{ve}{b}ms{e}" 
            else:
                self._text_representation = f"{LT}{vb}1{ve}{b}s{e}" 

        else:
            weeks,      remain  = divmod(self._time, SECONDS_IN_WEEK)  if max_unit in ["w"]                        else (0, self._time)
            days,       remain  = divmod(remain, SECONDS_IN_DAY)       if max_unit in ["w", "d"]                   else (0, remain)
            hours,      remain  = divmod(remain, SECONDS_IN_HOUR)      if max_unit in ["w", "d", "h"]              else (0, remain)
            minutes,    remain  = divmod(remain, SECONDS_IN_MINUTE)    if max_unit in ["w", "d", "h", "m"]         else (0, remain)
            seconds,    remain  = divmod(remain, 1.0)                  if max_unit in ["w", "d", "h", "m", "s"]    else (0, remain)

            if weeks > 99:
                prefix = GT
                weeks, days, hours, minutes, seconds = (99, 6, 23, 59, 59)
            elif days > 9999:
                prefix = GT
                days, hours, minutes, seconds = (9999, 23, 59, 59)
            elif hours > 9999999:
                prefix = GT
                hours, minutes, seconds = (9999999, 59, 59)
            elif minutes > 9999999999:
                prefix = GT
                minutes, seconds = (9999999999, 59)
            elif seconds > 9999999999999:
                prefix = GT
                seconds = 9999999999999
            else:
                prefix = ""

            if is_just_weeks_if_cap and prefix == GT:
                weeks = self._time / SECONDS_IN_WEEK
                weeks, _ = divmod(weeks, 1.0)  # rounding prevention

                if weeks > 9999999999999:
                    weeks = 9999999999999
                    prefix = GT
                else:
                    prefix = ""

                self._text_representation = f"{prefix}{vb}{weeks:.0f}{ve}{b}w{e}"
            else:
                self._text_representation = ""
                is_front = True

                if not is_front or weeks != 0:
                    self._text_representation += f"{prefix}{vb}{weeks:.0f}{ve}{b}w{e}"
                    is_front = False
                    prefix = ""

                if not is_front or days != 0:
                    self._text_representation += f"{prefix}{vb}{days:.0f}{ve}{b}d{e}" if is_front else f"{prefix}{vb}{days:01.0f}{ve}{b}d{e}"
                    is_front = False
                    prefix = ""

                if not is_front or hours != 0:
                    self._text_representation += f"{prefix}{vb}{hours:.0f}{ve}{b}h{e}" if is_front else f"{prefix}{vb}{hours:02.0f}{ve}{b}h{e}"
                    is_front = False
                    prefix = ""

                if not is_front or minutes != 0:
                    self._text_representation += f"{prefix}{vb}{minutes:.0f}{ve}{b}m{e}" if is_front else f"{prefix}{vb}{minutes:02.0f}{ve}{b}m{e}"
                    is_front = False
                    prefix = ""
        
                self._text_representation += f"{prefix}{vb}{seconds:.0f}{ve}{b}s{e}" if is_front else f"{prefix}{vb}{seconds:02.0f}{ve}{b}s{e}"

    def get_time(self) -> float:
        """
        Returns 
            Time in seconds.
        """
        return self._time

    def __str__(self) -> str:
        return self._text_representation


class FineExpPerHour:
    MAX_LENGTH_AFTER_FORMAT  : int   = 12
    # format:
    #      0 exp/h
    #    XXX exp/h
    #   XXXU exp/h
    #  X.XXU exp/h
    #  XX.XU exp/h
    #  -XXXU exp/h
    # -X.XXU exp/h
    # -XX.XU exp/h
                  
    # format for out of range:
    # <-XXXb exp/h
    #  >XXXb exp/h

    _exp_per_hour           : int
    _text_representation    : str

    def __init__(self, exp_per_hour : SupportsInt = 0, *, value_color : str | None = None, unit_color : str | None = None):
        """
        value_color
            None or color of all values. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...

        unit_color
            None or color of all unit symbols. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...
        """
        if not isinstance(exp_per_hour, int):
            self._exp_per_hour = int(exp_per_hour)
        else:
            self._exp_per_hour = exp_per_hour

        is_below_zero = self._exp_per_hour < 0

        sign = "-" if is_below_zero else ""
        exp_per_hour = abs(self._exp_per_hour)

        remain = 0
        unit = ""

        if exp_per_hour >= 1000:
            exp_per_hour, remain = divmod(exp_per_hour, 1000)
            unit = "k"

        if exp_per_hour >= 1000:
            exp_per_hour, remain = divmod(exp_per_hour, 1000)
            unit = "M"

        if exp_per_hour >= 1000:
            exp_per_hour, remain = divmod(exp_per_hour, 1000)
            unit = "B"

        if exp_per_hour >= 1000:
            exp_per_hour, remain = (999, 0)
            prefix = LT if is_below_zero else GT
        else:
            prefix = ""


        vb = f"<font color=\"{value_color}\">" if value_color else ""
        ve = "</font>" if value_color else ""

        b = f"<font color=\"{unit_color}\">" if unit_color else ""
        e = "</font>" if unit_color else ""

        if exp_per_hour < 10 and unit != "":
            self._text_representation = f"{prefix}{sign}{vb}{exp_per_hour}.{remain // 10:02}{ve}{b}{unit} exp/h{e}"
        elif exp_per_hour < 100 and unit != "":
            self._text_representation = f"{prefix}{sign}{vb}{exp_per_hour}.{remain // 100:01}{ve}{b}{unit} exp/h{e}"
        else:
            self._text_representation = f"{prefix}{sign}{vb}{exp_per_hour}{ve}{b}{unit} exp/h{e}"

    def get_exp_per_hour(self) -> int:
        return self._exp_per_hour

    def __str__(self) -> str:
        return self._text_representation

    
class FinePercent:
    MAX_LENGTH_AFTER_FORMAT : int       = 9
    # >+100.00%
    # <-100.00%

    _percent                : float
    _integer                : int       # in percent
    _2_dig_after_dot        : int       # in centipercent
    _text_representation    : str

    def __init__(self, percent : SupportsFloat = 0.0, *, is_sign = False, integer_color : str | None = None, two_dig_after_dot_color : str | None = None):
        """
        integer_color
            None or color of all values. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...

        two_dig_after_dot_color
            None or color of all unit symbols. 
            Can be name: "grey", "yellow", "red", "green", "blue", "white", ...
            Can be value: "#7F7F7F", "#FFFF00", ...
        """
        if not isinstance(percent, float):
            self._percent = float(percent)
        else:
            self._percent = percent

        self._integer = int(self._percent)
        self._2_dig_after_dot = int((self._percent - self._integer) * 100)

        ib = f"<font color=\"{integer_color}\">" if integer_color else ""
        ie = "</font>" if integer_color else ""

        db = f"<font color=\"{two_dig_after_dot_color}\">" if two_dig_after_dot_color else ""
        de = "</font>" if two_dig_after_dot_color else ""

        if is_sign:
            sign = "+" if self._percent >= 0 else "-"
        elif self._percent < 0:
            sign = "-"
        else:
            sign = ""

        if self._integer > 100:
            integer, two_dig_after_dot = (100, 00)
            prefix = GT
        elif self._integer < -100:
            integer, two_dig_after_dot = (100, 00)
            prefix = LT
        else:
            integer, two_dig_after_dot = (abs(self._integer), abs(self._2_dig_after_dot))
            prefix = ""

        self._text_representation = f"{prefix}{sign}{ib}{integer}{ie}.{db}{two_dig_after_dot:02}{de}%"
    
    def get_percent(self) -> float:
        return self._percent

    def get_integer(self) -> int:
        """
        Returns
            Signed value as percentage.
        """
        return self._integer
    
    def get_2_dig_after_dot(self) -> int:
        """
        Returns
            Signed value as centipercentage.
        """
        return self._2_dig_after_dot
    
    def __str__(self) -> str:
        return self._text_representation
