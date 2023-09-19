from time import time as _get_time

from typing import SupportsFloat, SupportsInt
from dataclasses import dataclass

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

        if self._time == float('inf'):
            self._text_representation = "never"
        else:
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
    
class FinePercent:
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

        self._text_representation = f"{sign}{ib}{abs(self._integer)}{ie}.{db}{abs(self._2_dig_after_dot):02}{de}%"
    
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
    
    def __repr__(self) -> str:
        return self._text_representation
    
@dataclass
class ExpThresholdInfo:
    level       : int
    base_exp    : int
    exp_to_next : int

class StopWatch:
    _start          : float     # in seconds
    _stop           : float     # in seconds
    _accumulator    : float     # in seconds
    _elapsed_time   : float     # in seconds

    def __init__(self, *, start : float = 0.0):
        """
        start
            Time from the epoch in seconds.
        """
        self.reset(start)

    def reset(self, *, start : float = 0.0):
        """
        start
            Time from the epoch in seconds.
        """
        self._start         = _get_time() if start is None else start
        self._stop          = self._start
        self._accumulator   = 0.0
        self._elapsed_time  = 0.0

    def update(self):
        self._stop = _get_time()
        self._accumulator += self._stop - self._start
        self._start = self._stop

        self._elapsed_time, self._accumulator = divmod(self._accumulator, 1)

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
    
class Measurer:
    _level                          : int
    _prev_info                      : ExpThresholdInfo

    _progress                       : float     # in percent
    _progress_in_exp                : int

    _progress_step                  : float     # in percent
    _progress_step_in_exp           : int   

    _progress_step_time             : float     # in seconds
    _exp_per_hour                   : int       

    _time_to_10_percent             : float     # in seconds
    _time_to_next_level             : float     # in seconds

    _is_update_fail                 : bool

    def __init__(self):
        self._level                         = 0
        self._prev_info                     = _find_exp_threshold_info(0)

        self._progress                      = 0.0
        self._progress_in_exp               = 0

        self._progress_step                 = 0.0
        self._progress_step_in_exp          = 0

        self._progress_step_time            = 0.0
        self._exp_per_hour                  = 0

        self._time_to_10_percent            = float('inf')
        self._time_to_next_level            = float('inf')

        self._is_gained_level               = False

        self._is_update_fail                = False

    def update(self, total_exp : int, elapsed_time : float):
        """
        elapsed_time
            In seconds.
        """
        if elapsed_time > 0.0:
            info = _find_exp_threshold_info(total_exp)

            self._is_gained_level = info.level > self._prev_info.level

            if info:
                self._level = info.level

                progress_in_exp = total_exp - info.base_exp                           
                progress        = (progress_in_exp / info.exp_to_next) * 100    

                if self._is_gained_level:
                    self._progress_step_in_exp  = progress_in_exp                               
                    self._progress_step         = progress                                   
                else:
                    self._progress_step_in_exp  = progress_in_exp - self._progress_in_exp
                    self._progress_step         = progress - self._progress

                self._progress_in_exp   = progress_in_exp
                self._progress          = progress

                if self._is_gained_level:
                    self._exp_per_hour       = 0
                    self._progress_step_time = 0.0

                    self._time_to_next_level = float('inf')
                    self._time_to_10_percent = float('inf')
                else:
                    self._progress_step_time = elapsed_time

                    hours = (elapsed_time  / _SECONDS_IN_HOUR) 
                    self._exp_per_hour = int(self._progress_step_in_exp / hours) # in seconds

                    exp_per_second = self._progress_step_in_exp / elapsed_time
                    if exp_per_second > 0.0:
                        self._time_to_next_level = (info.exp_to_next - self._progress_in_exp) / exp_per_second  # in seconds
                        self._time_to_10_percent = (info.exp_to_next / 10) / exp_per_second               # in seconds
                    else:
                        self._time_to_next_level = float('inf')
                        self._time_to_10_percent = float('inf')

                self._is_update_fail = False

                self._prev_info = info
            else:
                self._is_update_fail = True

    def get_progress(self) -> int:
        """
        Returns
            Current progress to next level in percent.
        """
        return self._progress
    
    def get_progress_step(self) -> float:
        """
        Returns
            Last progress step to next level in percent.
        """
        return self._progress_step
    
    def get_progress_step_in_exp(self) -> int:
        """
        Returns
            Last progress step to next level in experience.
        """
        return self._progress_step_in_exp
    
    def get_progress_step_time(self) -> float:
        """
        Returns
            Time of last progress step to next level in seconds.
        """
        return self._progress_step_time
    
    def get_time_to_10_percent(self) -> float:
        """
        Returns
            Estimated time in second needed to get 10 percent of current level exp.
        """
        return self._time_to_10_percent
    
    def get_time_to_next_level(self) -> float:
        """
        Returns
            Estimated time in second to next level.
        """
        return self._time_to_next_level
    
    def get_exp_per_hour(self) -> int:
        return self._exp_per_hour
    
    def get_level(self) -> int:
        return self._level
    
    def is_gained_level(self) -> bool:
        return self._is_gained_level
    
    def is_update_fail(self) -> bool:
        return self._is_update_fail
    
def _find_exp_threshold_info(exp : int) -> ExpThresholdInfo | None:
    for info in _EXP_THRESHOLD_INFO_TABLE:
        if exp < (info.base_exp + info.exp_to_next):
            return info 
    return None

_EXP_THRESHOLD_INFO_TABLE = (
    ExpThresholdInfo(1, 0, 525),
    ExpThresholdInfo(2, 525, 1235),
    ExpThresholdInfo(3, 1760, 2021),
    ExpThresholdInfo(4, 3781, 3403),
    ExpThresholdInfo(5, 7184, 5002),
    ExpThresholdInfo(6, 12186, 7138),
    ExpThresholdInfo(7, 19324, 10053),
    ExpThresholdInfo(8, 29377, 13804),
    ExpThresholdInfo(9, 43181, 18512),
    ExpThresholdInfo(10, 61693, 24297),
    ExpThresholdInfo(11, 85990, 31516),
    ExpThresholdInfo(12, 117506, 39878),
    ExpThresholdInfo(13, 157384, 50352),
    ExpThresholdInfo(14, 207736, 62261),
    ExpThresholdInfo(15, 269997, 76465),
    ExpThresholdInfo(16, 346462, 92806),
    ExpThresholdInfo(17, 439268, 112027),
    ExpThresholdInfo(18, 551295, 133876),
    ExpThresholdInfo(19, 685171, 158538),
    ExpThresholdInfo(20, 843709, 187025),
    ExpThresholdInfo(21, 1030734, 218895),
    ExpThresholdInfo(22, 1249629, 255366),
    ExpThresholdInfo(23, 1504995, 295852),
    ExpThresholdInfo(24, 1800847, 341805),
    ExpThresholdInfo(25, 2142652, 392470),
    ExpThresholdInfo(26, 2535122, 449555),
    ExpThresholdInfo(27, 2984677, 512121),
    ExpThresholdInfo(28, 3496798, 583857),
    ExpThresholdInfo(29, 4080655, 662181),
    ExpThresholdInfo(30, 4742836, 747411),
    ExpThresholdInfo(31, 5490247, 844146),
    ExpThresholdInfo(32, 6334393, 949053),
    ExpThresholdInfo(33, 7283446, 1100952),
    ExpThresholdInfo(34, 8384398, 1156712),
    ExpThresholdInfo(35, 9541110, 1333241),
    ExpThresholdInfo(36, 10874351, 1487491),
    ExpThresholdInfo(37, 12361842, 1656447),
    ExpThresholdInfo(38, 14018289, 1841143),
    ExpThresholdInfo(39, 15859432, 2046202),
    ExpThresholdInfo(40, 17905634, 2265837),
    ExpThresholdInfo(41, 20171471, 2508528),
    ExpThresholdInfo(42, 22679999, 2776124),
    ExpThresholdInfo(43, 25456123, 3061734),
    ExpThresholdInfo(44, 28517857, 3379914),
    ExpThresholdInfo(45, 31897771, 3723676),
    ExpThresholdInfo(46, 35621447, 4099570),
    ExpThresholdInfo(47, 39721017, 4504444),
    ExpThresholdInfo(48, 44225461, 4951099),
    ExpThresholdInfo(49, 49176560, 5430907),
    ExpThresholdInfo(50, 54607467, 5957868),
    ExpThresholdInfo(51, 60565335, 6528910),
    ExpThresholdInfo(52, 67094245, 7153414),
    ExpThresholdInfo(53, 74247659, 7827968),
    ExpThresholdInfo(54, 82075627, 8555414),
    ExpThresholdInfo(55, 90631041, 9353933),
    ExpThresholdInfo(56, 99984974, 10212541),
    ExpThresholdInfo(57, 110197515, 11142646),
    ExpThresholdInfo(58, 121340161, 12157041),
    ExpThresholdInfo(59, 133497202, 13252160),
    ExpThresholdInfo(60, 146749362, 14441758),
    ExpThresholdInfo(61, 161191120, 15731508),
    ExpThresholdInfo(62, 176922628, 17127265),
    ExpThresholdInfo(63, 194049893, 18635053),
    ExpThresholdInfo(64, 212684946, 20271765),
    ExpThresholdInfo(65, 232956711, 22044909),
    ExpThresholdInfo(66, 255001620, 23950783),
    ExpThresholdInfo(67, 278952403, 26019833),
    ExpThresholdInfo(68, 304972236, 28261412),
    ExpThresholdInfo(69, 333233648, 30672515),
    ExpThresholdInfo(70, 363906163, 33287878),
    ExpThresholdInfo(71, 397194041, 36118904),
    ExpThresholdInfo(72, 433312945, 39163425),
    ExpThresholdInfo(73, 472476370, 42460810),
    ExpThresholdInfo(74, 514937180, 46024718),
    ExpThresholdInfo(75, 560961898, 49853964),
    ExpThresholdInfo(76, 610815862, 54008554),
    ExpThresholdInfo(77, 664824416, 58473753),
    ExpThresholdInfo(78, 723298169, 63314495),
    ExpThresholdInfo(79, 786612664, 68516464),
    ExpThresholdInfo(80, 855129128, 74132190),
    ExpThresholdInfo(81, 929261318, 80182477),
    ExpThresholdInfo(82, 1009443795, 86725730),
    ExpThresholdInfo(83, 1096169525, 93748717),
    ExpThresholdInfo(84, 1189918242, 101352108),
    ExpThresholdInfo(85, 1291270350, 109524907),
    ExpThresholdInfo(86, 1400795257, 118335069),
    ExpThresholdInfo(87, 1519130326, 127813148),
    ExpThresholdInfo(88, 1646943474, 138033822),
    ExpThresholdInfo(89, 1784977296, 149032391),
    ExpThresholdInfo(90, 1934009687, 160890604),
    ExpThresholdInfo(91, 2094900291, 173648795),
    ExpThresholdInfo(92, 2268549086, 187372170),
    ExpThresholdInfo(93, 2455921256, 202153736),
    ExpThresholdInfo(94, 2658074992, 218041909),
    ExpThresholdInfo(95, 2876116901, 235163399),
    ExpThresholdInfo(96, 3111280300, 253547862),
    ExpThresholdInfo(97, 3364828162, 273358532),
    ExpThresholdInfo(98, 3638186694, 294631836),
    ExpThresholdInfo(99, 3932818530, 317515914),
    ExpThresholdInfo(100, 4250334444, 0),
)