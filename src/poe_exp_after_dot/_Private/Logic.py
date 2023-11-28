import re       as _re
import logging  as _logging
import numpy    as _numpy
import cv2      as _cv2
import easyocr  as _easyocr # type: ignore

from typing         import Any
from dataclasses    import dataclass
from time           import time as _get_time_since_epoch
from PIL            import ImageGrab as _ImageGrab

from PySide6.QtWidgets  import QWidget

from .Commons           import EXIT_FAILURE, EXIT_SUCCESS, time_unit_to_short, character_name_to_log_name
from .FineFormatters    import FineBareLevel, FineExp, FineExpPerHour, FinePercent, FineTime
from .Settings          import Settings
from .LogManager        import to_logger
from .CharacterRegister import CharacterRegister, Character
from .Measurer          import Measurer


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
    _settings           : Settings
    _measurer           : Measurer
    _character_register : CharacterRegister

    _reader             : _easyocr.Reader
    _is_fetch_failed    : bool

    def __init__(self, settings : Settings):
        self._settings = settings

        self._measurer = Measurer()

        self._reader = _easyocr.Reader(['en'], gpu = True, verbose = False)

        self._character_register = CharacterRegister(settings.get_val("_data_path", str))

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

        screenshot = _ImageGrab.grab()

        for widget in widgets_to_hide:
            widget.show()

        left    = cursor_x_in_screen + self._settings.get_val("_solved_pos_data.in_game_exp_tooltip_x_offset", int)
        right   = self._settings.get_val("_solved_pos_data.in_game_exp_tooltip_y", int)
        width   = self._settings.get_val("_solved_pos_data.in_game_exp_tooltip_width", int)
        height  = self._settings.get_val("_solved_pos_data.in_game_exp_tooltip_height", int)

        in_game_exp_tooltip_image = screenshot.crop((
            left,
            right,
            left + width,
            right + height,
        ))
        in_game_exp_tooltip_image = _cv2.cvtColor(_numpy.array(in_game_exp_tooltip_image), _cv2.COLOR_RGB2BGR) # converts image from Pillow format to OpenCV format

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

        if to_logger().isEnabledFor(_logging.DEBUG):
            to_logger().debug(f"Scanned In-Game Exp Tooltip Text: {full_text}")
            for text_fragment in text_fragments:
                to_logger().debug(text_fragment)
            to_logger().debug("---")

        match_ = _re.search(r"^.*?Current[ ]+Exp\:[ ]+([0-9,]+)[ ]+.*$", full_text)
        if match_:
            return int(match_.group(1).replace(",", ""))
        
        to_logger().error(f"Can't find current exp amount in In-Game Exp Tooltip. Scanned Text: \"{full_text}\"")

        return None
