from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass

import re
import os
import json
import logging
import numpy
import cv2
import easyocr # type: ignore

from datetime import datetime as _datetime
from time import time as _get_time_since_epoch
from PIL import ImageGrab

from PySide6.QtWidgets  import QWidget

from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, time_unit_to_short, character_name_to_log_name
from .FineFormatters    import FineBareLevel, FineExp, FineExpPerHour, FinePercent, FineTime
from .FineFormatters    import SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE, SECONDS_IN_WEEK
from .Settings          import Settings
from .LogManager        import to_logger
from .CharacterRegister import CharacterRegister, Character

def _float_to_proper_value(value : float) -> float | str:
    if value == float("inf"):
        return "inf"
    if value == float("-inf"):
        return "-inf"
    return value

@dataclass
class ExpThresholdInfo:
    level       : int
    base_exp    : int
    exp_to_next : int

    def to_dict(self) -> dict[str, Any]:
        return {
            "level"         : self.level,
            "base_exp"      : self.base_exp,
            "exp_to_next"   : self.exp_to_next,
        }
    
    @staticmethod
    def from_dict(dict_ : dict[str, Any]) -> "ExpThresholdInfo":
        return ExpThresholdInfo(
            int(dict_["level"]),
            int(dict_["base_exp"]),
            int(dict_["exp_to_next"]),
        )

EXP_THRESHOLD_INFO_TABLE = (
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

_REVERSED_EXP_THRESHOLD_INFO_TABLE = tuple(reversed(EXP_THRESHOLD_INFO_TABLE))

class ExpOutOfRange(Exception):
    pass

def find_exp_threshold_info(total_exp : int) -> ExpThresholdInfo:
    for info in _REVERSED_EXP_THRESHOLD_INFO_TABLE:
        if total_exp >= info.base_exp:
            if total_exp > (info.base_exp + info.exp_to_next):
                raise ExpOutOfRange(f"Total experience with value equal to {total_exp} is out of expected range.")
            return info 
    raise ExpOutOfRange(f"Total experience with value equal to {total_exp} is out of expected range.")

@dataclass
class Entry:
    total_exp               : int
    info                    : ExpThresholdInfo
    time_                   : float     # since epoch, in seconds

    is_other_level          : bool
    is_gained_level         : bool

    progress                : float     # in percent
    progress_in_exp         : int

    progress_step           : float     # in percent
    progress_step_in_exp    : int   

    progress_step_time      : float     # in seconds
    exp_per_hour            : int       

    time_to_10_percent      : float     # in seconds
    time_to_next_level      : float     # in seconds

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_exp"             : self.total_exp,
            "info"                  : self.info.to_dict(),
            "time_"                 : _float_to_proper_value(self.time_),

            "is_other_level"        : self.is_other_level,
            "is_gained_level"       : self.is_gained_level,

            "progress"              : _float_to_proper_value(self.progress),
            "progress_in_exp"       : self.progress_in_exp,

            "progress_step"         : _float_to_proper_value(self.progress_step),
            "progress_step_in_exp"  : self.progress_step_in_exp,

            "progress_step_time"    : _float_to_proper_value(self.progress_step_time),
            "exp_per_hour"          : self.exp_per_hour,

            "time_to_10_percent"    : _float_to_proper_value(self.time_to_10_percent),
            "time_to_next_level"    : _float_to_proper_value(self.time_to_next_level),
        }
    
    @staticmethod
    def from_dict(dict_ : dict[str, Any]) -> "Entry":
        return Entry(
            total_exp               = int(dict_["total_exp"]),
            info                    = ExpThresholdInfo.from_dict(dict_["info"]),
            time_                   = float(dict_["time_"]),

            is_other_level          = bool(dict_["is_other_level"]),
            is_gained_level         = bool(dict_["is_gained_level"]),

            progress                = float(dict_["progress"]),
            progress_in_exp         = int(dict_["progress_in_exp"]),

            progress_step           = float(dict_["progress_step"]),
            progress_step_in_exp    = int(dict_["progress_step_in_exp"]),

            progress_step_time      = float(dict_["progress_step_time"]),
            exp_per_hour            = int(dict_["exp_per_hour"]),

            time_to_10_percent      = float(dict_["time_to_10_percent"]),
            time_to_next_level      = float(dict_["time_to_next_level"]),
        )


class Register:
    _entries    : list[Entry]
    _index      : int           # -1 - before first, no entry

    def __init__(self):
        self._entries = []
        self._index = -1

    def load(self, file_name : str):
        with open(file_name, "r") as file:
            self.load_from_str(file.read())

    def save(self, file_name : str):
        """
        file_name : None
            Uses last used name either by 'load', 'save' or 'switch'.
        """
        with open(file_name, "w") as file:
            file.write(self.export_to_str())

    def load_from_str(self, exp_data_text : str):
        self._entries = []

        exp_data = json.loads(exp_data_text)
        for entry in exp_data:
            self._entries.append(Entry.from_dict(entry))

        self._index = len(self._entries) - 1

    def export_to_str(self) -> str:
        exp_data = []
        for entry in self._entries:
            exp_data.append(entry.to_dict())

        return json.dumps(exp_data, indent = 4)

    def remove_all_after_current(self):
        if self._index > -1:
            self._entries = self._entries[:self._index + 1]

    def add_new(self, entry : Entry):
        self._index += 1
        self._entries = self._entries[:self._index] + [entry]

    def go_to_previous(self):
        if self._index >= 0: 
            self._index -= 1

    def go_to_next(self):
        if (self._index + 1) < len(self._entries):
            self._index += 1

    def go_to_last(self):
        if self._index >= -1:
            self._index = len(self._entries) - 1

    def go_to_first(self):
        if self._index >= 0:
            self._index = 0

    def go_to_before_first(self):
        self._index = -1
    
    def to_current(self) -> Entry | None:
        return self._entries[self._index] if self._index >= 0 else None
    
    def is_any(self) -> int:
        return len(self._entries) > 0
    
    def is_first(self) -> bool:
        return self._index == 0
    
    def is_before_first(self) -> bool:
        return self._index == -1
    
    def is_last(self) -> bool:
        return self._index >= 0 and self._index == (len(self._entries) - 1)
    
    def get_number(self) -> int:
        return len(self._entries)
    
    def get_current_index(self) -> int | None:
        """
        Returns
            0..N    - Index of current entry.
            None    - There is no entry.
        """
        return self._index if self._index >= 0 else None
    
    def get_current_page(self) -> int:
        """
        Returns
            0..N    - Page of current entry.
        """
        return self._index + 1

    
_EMPTY_ENTRY = Entry(
    total_exp               = 0,
    info                    = ExpThresholdInfo(0, 0, 0),
    time_                   = 0.0,

    is_other_level          = False,
    is_gained_level         = False,

    progress                = 0.0,
    progress_in_exp         = 0,

    progress_step           = 0.0,
    progress_step_in_exp    = 0,

    progress_step_time      = 0.0,
    exp_per_hour            = 0,

    time_to_10_percent      = float('inf'),
    time_to_next_level      = float('inf')
)

class Measurer:
    _register           : Register
    _is_update_fail     : bool

    def __init__(self):
        self._register = Register()
        self._is_update_fail = False

    def load_exp_data(self, file_name : str):
        self._register.load(file_name)

    def save_exp_data(self, file_name : str):
        self._register.save(file_name)
        
    def update(self, total_exp : int, time_ : float):
        """
        time_
            In seconds. Since epoch.
        """
        previous = self._register.to_current()

        try:
            info = find_exp_threshold_info(total_exp)
        except ExpOutOfRange as exception:
            to_logger().error(f"Update failed. f{str(exception)}")
            self._is_update_fail = True
        else:
            if previous is None:
                is_other_level  = True
                is_gained_level = False
            else:
                is_other_level  = info.level != previous.info.level
                is_gained_level = info.level > previous.info.level

            progress_in_exp = total_exp - info.base_exp  
            if progress_in_exp == 0:
                progress = 0.0
            else:
                progress = (progress_in_exp / info.exp_to_next) * 100    

            if is_other_level:
                progress_step_in_exp    = progress_in_exp                               
                progress_step           = progress   
            
                exp_per_hour            = 0
                progress_step_time      = 0.0

                time_to_next_level      = float('inf')
                time_to_10_percent      = float('inf')
            else:
                elapsed_time            = time_ - previous.time_                        # type: ignore[union-attr]

                progress_step_in_exp    = progress_in_exp - previous.progress_in_exp    # type: ignore[union-attr]
                progress_step           = progress - previous.progress                  # type: ignore[union-attr]

                exp_per_hour            = int(progress_step_in_exp * SECONDS_IN_HOUR / elapsed_time)
                progress_step_time      = elapsed_time

                if progress_step_in_exp > 0:
                    time_to_next_level = (info.exp_to_next - progress_in_exp) * elapsed_time / progress_step_in_exp  
                    time_to_10_percent = (info.exp_to_next * elapsed_time) / (progress_step_in_exp * 10)
                else:
                    time_to_next_level = float('inf')
                    time_to_10_percent = float('inf')

            self._register.add_new(Entry(
                total_exp               = total_exp,
                info                    = info,     
                time_                   = time_,
                is_other_level          = is_other_level,  
                is_gained_level         = is_gained_level,               
                progress                = progress,               
                progress_in_exp         = progress_in_exp,
                progress_step           = progress_step,
                progress_step_in_exp    = progress_step_in_exp,
                progress_step_time      = progress_step_time,
                exp_per_hour            = exp_per_hour,
                time_to_10_percent      = time_to_10_percent,
                time_to_next_level      = time_to_next_level
            ))

            to_logger().debug(f"entry={self._register.to_current()}")
            self._is_update_fail = False

    def _to_entry_safe(self) -> Entry:
        """
        Returns
            Current entry if exists.
            Empty entry if current entry do not exist.
        """
        entry = self._register.to_current()
        return entry if entry is not None else _EMPTY_ENTRY
    
    def is_entry(self) -> bool:
        """
        Returns
            True    - If current entry exists.
            False   - Otherwise.
        """
        return self._register.to_current() is not None

    def get_total_exp(self) -> int:
        return self._to_entry_safe().total_exp 

    def get_progress(self) -> float:
        """
        Returns
            Current progress to next level in percent.
        """
        return self._to_entry_safe().progress
    
    def get_progress_step(self) -> float:
        """
        Returns
            Last progress step to next level in percent.
        """
        return self._to_entry_safe().progress_step
    
    def get_progress_step_in_exp(self) -> int:
        """
        Returns
            Last progress step to next level in experience.
        """
        return self._to_entry_safe().progress_step_in_exp
    
    def get_progress_step_time(self) -> float:
        """
        Returns
            Time of last progress step to next level in seconds.
        """
        return self._to_entry_safe().progress_step_time
    
    def get_time_to_10_percent(self) -> float:
        """
        Returns
            Estimated time in second needed to get 10 percent of current level exp.
        """
        return self._to_entry_safe().time_to_10_percent
    
    def get_time_to_next_level(self) -> float:
        """
        Returns
            Estimated time in second to next level.
        """
        return self._to_entry_safe().time_to_next_level
    
    def get_exp_per_hour(self) -> int:
        return self._to_entry_safe().exp_per_hour
    
    def get_level(self) -> int:
        return self._to_entry_safe().info.level
    
    def is_gained_level(self) -> bool:
        return self._to_entry_safe().is_gained_level
    
    def get_time_since_epoch(self) -> float:
        return self._to_entry_safe().time_
    
    def get_date_str(self, *, is_empty_str_when_epoch = False) -> str:
        time_ = self._to_entry_safe().time_
        if time_ == 0.0 and is_empty_str_when_epoch:
            return "" 
        return _datetime.fromtimestamp(time_).strftime("%Y/%m/%d %H:%M:%S")
    
    def is_update_fail(self) -> bool:
        return self._is_update_fail
    
    ### entry navigation ###
    def get_number_of_entries(self) -> int:
        return self._register.get_number()
    
    def get_current_entry_index(self) -> int | None:
        return self._register.get_current_index()
    
    def get_current_entry_page(self) -> int:
        return self._register.get_current_page()
    
    def go_to_next_entry(self):
        self._register.go_to_next()

    def go_to_previous_entry(self):
        self._register.go_to_previous()

    def go_to_before_first_entry(self):
        self._register.go_to_before_first()

    def go_to_first_entry(self):
        self._register.go_to_first()

    def go_to_last_entry(self):
        self._register.go_to_last()

    def remove_all_after_current_entry(self):
        self._register.remove_all_after_current()


@dataclass
class PosData:
    info_board_x                    : int
    info_board_bottom               : int

    control_region_x                     : int
    control_region_y                     : int
    control_region_width                 : int
    control_region_height                : int

    in_game_exp_bar_x               : int
    in_game_exp_bar_y               : int
    in_game_exp_bar_width           : int
    in_game_exp_bar_height          : int

    in_game_exp_tooltip_x_offset    : int # from cursor pos
    in_game_exp_tooltip_y           : int 
    in_game_exp_tooltip_width       : int 
    in_game_exp_tooltip_height      : int 


class Point:
    x : int
    y : int

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f"PointI(x={self.x}, y={self.y})"

class Polygon:
    lb : Point
    rb : Point
    rt : Point
    lt : Point

    def __init__(self, data):
        # corners
        self.lb = Point(data[0][0], data[0][1]) # left bottom
        self.rb = Point(data[1][0], data[1][1]) # right bottom
        self.rt = Point(data[2][0], data[2][1]) # right top
        self.lt = Point(data[3][0], data[3][1]) # left top

    def __str__(self):
        return f"Polygon(lb={self.lb}, rb={self.rb}, rt={self.rt}, lt={self.lt})" 

class TextFragment:
    text    : str
    polygon : Polygon

    def __init__(self, data):
        self.text       = data[1]
        self.polygon    = Polygon(data[0])

    def __str__(self):
        return f"TextFragment(text=\"{self.text}\", polygon={self.polygon})" 
    
    def __repr__(self):
        return self.__str__()

class Logic:
    _settings   : Settings
    _pos_data   : PosData
    _measurer   : Measurer
    _character_register : CharacterRegister

    _reader     : easyocr.Reader

    _is_fetch_failed : bool

    def __init__(self, settings : Settings):
        self._settings = settings

        def get_val(resolution_name : str, data_name : str) -> int:
            value = settings.try_get_val(f"pos_data._command_line_custom.{data_name}", int)
            if value is not None:
                return value
            return settings.get_val(f"pos_data.{resolution_name}.{data_name}", int) 

        self._pos_data = PosData(
            info_board_x                    = get_val("1920x1080", "info_board_x"),       
            info_board_bottom               = get_val("1920x1080", "info_board_bottom"),  

            control_region_x                     = get_val("1920x1080", "control_region_x"),        
            control_region_y                     = get_val("1920x1080", "control_region_y"),        
            control_region_width                 = get_val("1920x1080", "control_region_width"),    
            control_region_height                = get_val("1920x1080", "control_region_height"),   
        
            in_game_exp_bar_x               = get_val("1920x1080", "in_game_exp_bar_x"),  
            in_game_exp_bar_y               = get_val("1920x1080", "in_game_exp_bar_y"),      
            in_game_exp_bar_width           = get_val("1920x1080", "in_game_exp_bar_width"),  
            in_game_exp_bar_height          = get_val("1920x1080", "in_game_exp_bar_height"), 

            in_game_exp_tooltip_x_offset    = get_val("1920x1080", "in_game_exp_tooltip_x_offset"),
            in_game_exp_tooltip_y           = get_val("1920x1080", "in_game_exp_tooltip_y"),       
            in_game_exp_tooltip_width       = get_val("1920x1080", "in_game_exp_tooltip_width"),   
            in_game_exp_tooltip_height      = get_val("1920x1080", "in_game_exp_tooltip_height"),  
        )

        self._measurer = Measurer()

        self._reader = easyocr.Reader(['en'], gpu = True, verbose = False)

        self._character_register = CharacterRegister(settings.get_val("data_path", str))

        self._is_fetch_failed = False

    def to_character_register(self):
        return self._character_register

    def scan_and_load_character(self):
        self._character_register.add_character("")
        self._character_register.scan_for_characters()

        to_logger().info(f"Scanned for character data.")

        self.load_character()

    def load_character(self):
        self._load_character()

        to_logger().info(f"Loaded character data of {character_name_to_log_name(self.get_character_name())}.")

    def switch_character(self, character_name : str):
        current_character_name = self.get_character_name()
        self._save_character()
        self._settings.set_val("character_name", character_name, str)
        self._load_character()

        to_logger().info(f"Switched character data from {character_name_to_log_name(current_character_name)} to {character_name_to_log_name(self.get_character_name())}. (Switch = Save Current & Load Existing/New)")

    def save_character(self):
        self._save_character()

        to_logger().info(f"Saved character data of {character_name_to_log_name(self.get_character_name())}.")

    def get_character_name(self) -> str:
        """
        Returns
            Name of currently selected character.
        """
        return self._settings.get_val("character_name", str)
    
    def to_character(self) -> Character:
        return self._character_register.to_character(self.get_character_name())

    def get_info_board_text_parameters(self) -> dict[str, Any]:
        max_unit = time_unit_to_short(self._settings.get_val("time_max_unit", str))

        return {
            "page"                  : self._measurer.get_current_entry_page(),
            "number"                : self._measurer.get_number_of_entries(),
            "date"                  : self._measurer.get_date_str(is_empty_str_when_epoch = True),

            "font_name"             : self._settings.get_val("font.name", str),
            "font_size"             : self._settings.get_val("font.size", int),

            "level"                 : FineBareLevel(self._measurer.get_level()),
            "progress"              : FinePercent(self._measurer.get_progress(), integer_color = "#F8CD82", two_dig_after_dot_color = "#7F7FFF"),
            "exp"                   : FineExp(self._measurer.get_total_exp(), unit_color = "#9F9F9F"),
            "progress_step"         : FinePercent(self._measurer.get_progress_step(), is_sign = True, integer_color = "#7FFFFF", two_dig_after_dot_color = "#7FFFFF"),
            "progress_step_time"    : FineTime(self._measurer.get_progress_step_time(), max_unit = max_unit, unit_color = "#8F8F8F", never_color = "#FF4F1F"),
            "exp_per_hour"          : FineExpPerHour(self._measurer.get_exp_per_hour(), value_color = "#6FFF6F", unit_color = "#9F9F9F"),

            "time_to_10_percent"    : FineTime(self._measurer.get_time_to_10_percent(), max_unit = max_unit, unit_color = "#9F9F9F", never_color = "#FF4F1F"),
            "time_to_next_level"    : FineTime(self._measurer.get_time_to_next_level(), max_unit = max_unit, unit_color = "#9F9F9F", never_color = "#FF4F1F"),
            "hint_begin"            : "<font size=10px color=\"#7f7f7f\">",
            "hint_end"              : "</font>",
            "h"                     : "#",
            "y"                     : "-",
            "nothing"               : "",
        }

    def to_settings(self) -> Settings:
        return self._settings

    def to_measurer(self) -> Measurer:
        return self._measurer
    
    def to_pos_data(self) -> PosData:
        return self._pos_data
        
    def measure(self, cursor_x_in_screen : int, cursor_y_in_screen : int, widgets_to_hide : list[QWidget]):
        time_ = _get_time_since_epoch()

        current_exp = self._fetch_exp(cursor_x_in_screen, cursor_y_in_screen, widgets_to_hide)

        if current_exp is None:
            self._is_fetch_failed = True
        else:
            self._measurer.update(current_exp, time_)
            self._is_fetch_failed = False

    def is_fetch_failed(self) -> bool:
        return self._is_fetch_failed
    
    def _load_character(self):
        character = self._character_register.to_character(self.get_character_name())
        self._measurer.load_exp_data(character.get_exp_data_file_name())

    def _save_character(self):
        self._measurer.save_exp_data(self.to_character().get_exp_data_file_name())

    def _fetch_exp(self, cursor_x_in_screen : int, cursor_y_in_screen: int, widgets_to_hide : list[QWidget]) -> int | None:
        """
        Returns
            Current experience.
        """
        for widget in widgets_to_hide:
            widget.hide()

        screenshot = ImageGrab.grab()

        for widget in widgets_to_hide:
            widget.show()

        left    = cursor_x_in_screen + self._pos_data.in_game_exp_tooltip_x_offset
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

        text_fragments = [TextFragment(text_fragment) for text_fragment in self._reader.readtext(in_game_exp_tooltip_image)]

        min_text_height = in_game_exp_tooltip_image.shape[0] 
        
        # used to fix little misalignment on Y axis 
        for text_fragment in text_fragments:
            min_text_height = min(text_fragment.polygon.lt.y - text_fragment.polygon.lb.y, min_text_height)

        width = in_game_exp_tooltip_image.shape[1] # type: ignore

        def extract_comparison_key(text_fragment : TextFragment):
            p = text_fragment.polygon.lb # position of left bottom corner
            return p.x + width * (p.y // min_text_height)

        text_fragments.sort(key = extract_comparison_key)

        full_text = ""
        for text_fragment in text_fragments:
            full_text += text_fragment.text + " "

        if to_logger().isEnabledFor(logging.DEBUG):
            to_logger().debug(f"Scanned In-Game Exp Tooltip Text: {full_text}")
            for text_fragment in text_fragments:
                to_logger().debug(text_fragment)
            to_logger().debug("---")

        match_ = re.search(r"^.*?Current[ ]+Exp\:[ ]+([0-9,]+)[ ]+.*$", full_text)
        if match_:
            return int(match_.group(1).replace(",", ""))
        
        to_logger().error(f"Can't find current exp amount in In-Game Exp Tooltip. Scanned Text: \"{full_text}\"")

        return None
