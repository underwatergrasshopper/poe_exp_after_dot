
import json as _json

from datetime           import datetime as _datetime
from typing             import Any
from dataclasses        import dataclass

from .FineFormatters    import SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE, SECONDS_IN_WEEK
from .Settings          import Settings
from .LogManager        import to_logger
from .ExpThresholdInfo  import ExpThresholdInfo, EXP_THRESHOLD_INFO_TABLE


def _float_to_proper_value(value : float) -> float | str:
    if value == float("inf"):
        return "inf"
    if value == float("-inf"):
        return "-inf"
    return value


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

        exp_data = _json.loads(exp_data_text)
        for entry in exp_data:
            self._entries.append(Entry.from_dict(entry))

        self._index = len(self._entries) - 1

    def export_to_str(self) -> str:
        exp_data = []
        for entry in self._entries:
            exp_data.append(entry.to_dict())

        return _json.dumps(exp_data, indent = 4)

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