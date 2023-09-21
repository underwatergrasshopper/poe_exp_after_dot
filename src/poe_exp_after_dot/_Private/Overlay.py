from time import time as _get_time

from typing import SupportsFloat, SupportsInt, Sequence
from dataclasses import dataclass

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QColor, QMouseEvent, QIcon, QAction, QCloseEvent
from PySide6.QtCore import QPoint, QRect

import os
import re
import numpy
import cv2
import easyocr
import ctypes

from PIL import ImageGrab

_SECONDS_IN_MINUTE   = 60
_SECONDS_IN_HOUR     = 60 * _SECONDS_IN_MINUTE
_SECONDS_IN_DAY      = 24 * _SECONDS_IN_HOUR
_SECONDS_IN_WEEK     = 7  * _SECONDS_IN_DAY

def _pad_to_length(text : str, length : int):
        """
        If 'text' is shorter than 'length', then adds padding to front of 'text', until length of text is equal to 'length'.
        If 'text' is longer than 'length', then shorts 'text', until length of text is equal to 'length'.
        """
        return text.rjust(length)[:length]

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

        if level < 0:
            self._text_representation = "<0"
        elif level > 100:
            self._text_representation = ">100"
        else:
            self._text_representation = str(self._level)

    def get_level(self) -> int:
        return self._level

    def __str__(self) -> str:
        return self._text_representation
    
    def __repr__(self) -> str:
        return self._text_representation

class FineTime:
    LENGTH_AFTER_FORMAT     : int   = 15
    # format for out of range:
    # >99w6d23h59m59s
    # >9999d23h59m59s
    # >9999999h59m59s
    # >9999999999m59s
    # >9999999999999s
    #             <0s
    # format for below measurement:
    #             <1s

    _time                   : float
    _text_representation    : str

    def __init__(
            self, 
            time_ : SupportsFloat = 0.0, 
            max_unit : str = "w", 
            *, 
            value_color : str | None = None, 
            unit_color : str | None = None, 
            never_color : str | None = None
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
            self._text_representation = f"<{vb}0{ve}{b}s{e}" 

        elif self._time == 0.0:
            self._text_representation = f"{vb}0{ve}{b}s{e}" 

        elif self._time < 1.0:
            self._text_representation = f"<{vb}1{ve}{b}s{e}" 

        else:
            weeks,      remain  = divmod(self._time, _SECONDS_IN_WEEK)  if max_unit in ["w"]                else (0, self._time)
            days,       remain  = divmod(remain, _SECONDS_IN_DAY)       if max_unit in ["w", "d"]           else (0, remain)
            hours,      remain  = divmod(remain, _SECONDS_IN_HOUR)      if max_unit in ["w", "d", "h"]      else (0, remain)
            minutes,    seconds = divmod(remain, _SECONDS_IN_MINUTE)    if max_unit in ["w", "d", "h", "m"] else (0, remain)

            if weeks > 99:
                prefix = ">"
                weeks, days, hours, minutes, seconds = (99, 6, 23, 59, 59)
            elif days > 9999:
                prefix = ">"
                days, hours, minutes, seconds = (9999, 23, 59, 59)
            elif hours > 9999999:
                prefix = ">"
                hours, minutes, seconds = (9999999, 59, 59)
            elif minutes > 9999999999:
                prefix = ">"
                minutes, seconds = (9999999999, 59)
            elif seconds > 9999999999999:
                prefix = ">"
                seconds = 9999999999999
            else:
                prefix = ""

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
        self.reset(start = start)

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

            if info:
                self._is_gained_level = info.level > self._prev_info.level

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

    def get_progress(self) -> float:
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

@dataclass
class PosData:
    control_bar_x                   : int
    control_bar_y                   : int
    control_bar_width               : int
    control_bar_height              : int

    exp_bar_y_offset                : int # from control bar position
    exp_bar_height                  : int

    in_game_full_exp_region_y       : int
    in_game_full_exp_region_height  : int

    in_game_exp_tooltip_x_offset    : int # from cursor pos
    in_game_exp_tooltip_y           : int 
    in_game_exp_tooltip_width       : int 
    in_game_exp_tooltip_height      : int 


def get_pos_data(resolution_width : int, resolution_height : int) -> PosData | None:
    """
    Returns
        PosData for resolution if resolution is supported.
        None if resolution is not supported.
    """
    match (resolution_width, resolution_height):
        case (1920, 1080):
            return PosData(
                control_bar_x                   = 551,
                control_bar_y                   = 1059,
                control_bar_width               = 820,
                control_bar_height              = 21,
            
                exp_bar_y_offset                = 10,
                exp_bar_height                  = 5,
                
                in_game_full_exp_region_y       = 1056,
                in_game_full_exp_region_height  = 24,

                in_game_exp_tooltip_x_offset    = 64,
                in_game_exp_tooltip_y           = 1007,
                in_game_exp_tooltip_width       = 446,
                in_game_exp_tooltip_height      = 73,
            )
        
    return None


class ExpBar(QWidget):
    _pos_data : PosData
    _width    : int

    def __init__(self, pos_data : PosData):
        super().__init__()

        self._pos_data = pos_data

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        self.setWindowOpacity(0.5)

        # background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(127, 127, 255))
        self.setPalette(palette)
        
        self.set_area(0.0, is_try_show = False)

    def set_area(self, ratio : float, *, is_try_show = True):
        """
        ratio
            Value from range 0 to 1.
        """
        self._width = int(self._pos_data.control_bar_width * ratio)

        self.setGeometry(QRect(
            self._pos_data.control_bar_x,
            self._pos_data.control_bar_y + self._pos_data.exp_bar_y_offset,
            max(1, self._width),
            self._pos_data.exp_bar_height,
        ))

        if is_try_show:
            if self._width >= 1:
                self.show()
            else:
                self.hide()

    def try_show(self):
        if self._width >= 1:
            self.show()


class ExpInfoBoard(QWidget):
    _pos_data   : PosData
    _prev_pos   : QPoint | None

    def __init__(self, pos_data : PosData, font_name = "Consolas", font_size = 16):
        """
        font_size
            In pixels.
        """
        super().__init__()

        self._pos_data = pos_data

        self._prev_pos = None

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        # background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)

        # transparency
        self.setWindowOpacity(0.7)

        # text
        self._label = QLabel("", self)
        self._label.setStyleSheet(f"font: {font_size}px {font_name}; color: white;")
        # NOTE: This is crucial. Prevents from blocking mouseReleaseEvent for parent widget.
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) 
        self.set_description("Click on in-game exp bar to receive data.<br>Ctrl + Shift + LMB to move this board.")

        self.oldPos = self.pos()

    def set_description(self, description, is_lock_left_bottom = False):
        if is_lock_left_bottom:
            rect = self.geometry()
            x = rect.x()
            bottom = rect.y() + rect.height()
        else:
            x = self._pos_data.control_bar_x
            bottom = self._pos_data.in_game_full_exp_region_y

        self._label.setText(description)
        self._label.adjustSize()
        self.adjustSize()
        
        pos = self.pos()
        pos.setX(x)
        pos.setY(bottom - self._label.height())
        self.move(pos)
    
    def mousePressEvent(self, event : QMouseEvent):
        # 'Ctrl + Shift + LMB' to move board (order matter)
        if event.button() == Qt.MouseButton.LeftButton and QApplication.keyboardModifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self._prev_pos = event.globalPos()

    def mouseReleaseEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._prev_pos = None

    def mouseMoveEvent(self, event : QMouseEvent):
        if self._prev_pos is not None:
            offset = QPoint(event.globalPos() - self._prev_pos)
            if offset:
                self.move(self.x() + offset.x(), self.y() + offset.y())
                self._prev_pos = event.globalPos()

class ControlBar(QMainWindow):
    _pos_data           : PosData
    _measurer           : Measurer
    _stop_watch         : StopWatch
    _exp_bar            : ExpBar
    _exp_info_board     : ExpInfoBoard

    def __init__(self, pos_data : PosData, measurer : Measurer, stop_watch : StopWatch):
        super().__init__()

        self._pos_data      = pos_data
        self._measurer      = measurer
        self._stop_watch    = stop_watch

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        self.setWindowOpacity(0.01)

        self.setGeometry(QRect(
            self._pos_data.control_bar_x,
            self._pos_data.control_bar_y,
            self._pos_data.control_bar_width,
            self._pos_data.control_bar_height,
        ))

        self._exp_bar = ExpBar(self._pos_data)
        self._exp_info_board = ExpInfoBoard(self._pos_data)

    def showEvent(self, event):
        self._exp_bar.try_show()
        self._exp_info_board.show()

    def hideEvent(self, event):
        self._exp_bar.hide()
        self._exp_info_board.hide()

    def mousePressEvent(self, event : QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            user32 = ctypes.windll.user32
            window_handle = user32.FindWindowW(None, "Path of Exile")
            if window_handle:
                user32.SetForegroundWindow(window_handle)
      
            self._stop_watch.update()

            pos = QPoint(event.x(), event.y())
            pos = self.mapToGlobal(pos)

            total_exp = self.fetch_exp(pos.x(), pos.y())

            self._measurer.update(total_exp, self._stop_watch.get_elapsed_time())

            level               = self._measurer.get_level()
            progress            = FinePercent(self._measurer.get_progress(), integer_color = "#F8CD82", two_dig_after_dot_color = "#7F7FFF")
            progress_step       = FinePercent(self._measurer.get_progress_step(), is_sign = True, integer_color = "#FFFF7F", two_dig_after_dot_color = "#FFFF7F")
            progress_step_time  = FineTime(self._measurer.get_progress_step_time(), max_unit = "h", unit_color = "#8F8F8F", never_color = "#FF4F1F")
            exp_per_hour        = FineExpPerHour(self._measurer.get_exp_per_hour(), value_color = "#6FFF6F", unit_color = "#9F9F9F")
            time_to_10_percent  = FineTime(self._measurer.get_time_to_10_percent(), max_unit = "h", unit_color = "#9F9F9F", never_color = "#FF4F1F")
            time_to_next_level  = FineTime(self._measurer.get_time_to_next_level(), max_unit = "h", unit_color = "#9F9F9F", never_color = "#FF4F1F")

            description = (
                f"LVL {level} {progress}<br>"
                f"{progress_step} in {progress_step_time}<br>"
                f"{exp_per_hour}<br>"
                f"10% in {time_to_10_percent}<br>"
                f"next in {time_to_next_level}"
            )

            ratio = self._measurer.get_progress()
            ratio = ratio - int(ratio)

            self._exp_bar.set_area(ratio)
            self._exp_info_board.set_description(description, is_lock_left_bottom = True)

    def fetch_exp(self, x : int, y: int) -> int:
        """
        x
            Position of cursor on X axis in screen.
        y
            Position of cursor on Y axis in screen.
        Returns
            Current experience.
        """
        self.hide()
        screenshot = ImageGrab.grab()
        self.show()

        left    = x + self._pos_data.in_game_exp_tooltip_x_offset
        right   = self._pos_data.in_game_exp_tooltip_y
        width   = self._pos_data.in_game_exp_tooltip_width
        height  = self._pos_data.in_game_exp_tooltip_height

        in_game_exp_tooltip_image = screenshot.crop((
            left,
            right,
            left + width,
            right + height,
        ))
        in_game_exp_tooltip_image = cv2.cvtColor(numpy.array(in_game_exp_tooltip_image), cv2.COLOR_RGB2BGR) # converts image from Pillow format to OpenCV format

        reader = easyocr.Reader(['en'], gpu = True, verbose=False)

        text_fragments= reader.readtext(in_game_exp_tooltip_image)

        width = in_game_exp_tooltip_image.shape[1]

        def extract_comparison_key(text_fragment):
            pos = text_fragment[0][0]
            return pos[0] + width * pos[1]

        text_fragments.sort(key = extract_comparison_key)

        full_text = ""
        for text_fragment in text_fragments:
            full_text += text_fragment[1] + " "

        exp = 0
        match_ = re.search(r"^.*?Current[ ]+Exp\:[ ]+([0-9,]+)[ ]+.*$", full_text)
        if match_:
            exp = int(match_.group(1).replace(",", ""))

        return exp
    
    def closeEvent(self, event : QCloseEvent) -> None:
        pass

    
class TrayMenu(QSystemTrayIcon):
    _menu           : QMenu
    _quit_action    : QAction

    def __init__(self, app : QApplication):
        super().__init__()

        icon_file_name =  os.path.abspath(os.path.dirname(__file__) + "/../assets/icon.png")
        self.setIcon(QIcon(icon_file_name))

        self._menu = QMenu()
        self._quit_action = QAction("Quit")
        self._quit_action.triggered.connect(app.quit)
        self._menu.addAction(self._quit_action)

        self.setContextMenu(self._menu)

class Overlay:
    def __init__(self):
        pass

    def main(self, argv : list[str]):
        width, height = (1920, 1080)
        pos_data = get_pos_data(width, height)
        if not pos_data:
            raise RuntimeError(f"Can not receive position data for resolution: {width}x{height}.")

        measurer = Measurer()
        stop_watch = StopWatch()

        app = QApplication(argv)

        control_bar = ControlBar(pos_data, measurer, stop_watch)
        control_bar.show()

        tray_menu = TrayMenu(app)
        tray_menu.show()

        result_code = app.exec_()