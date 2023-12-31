import os   as _os
import json as _json

from typing import Any, Type, Union
from copy   import deepcopy as _deepcopy

from .Commons import merge_on_all_levels as _merge_on_all_levels


ValueType   = Union[bool, int, float, str, list["ValueType"], dict[str, "ValueType"]]


class Settings:
    """
    Stores values in two spaces:
    persistent space    - For being loaded from file and saved into file and used in package.
    temporal space      - For being used only inside package. Is not saved to file.

    Each value name can have namespace.

    <name>
        (<namespace>\\.)*<variable_name>
        
    <namespace>
        <level_name>(\\.<level_name>)*

    Example of value name with namespace: 'ui.area.width'.
    """
    _persistent         : dict[str, Any]
    _temporal           : dict[str, Any]

    def __init__(self):
        self._temporal  = {}
        self._persistent  = {}
        
    def load(self, file_name : str):
        """
        Loads values to both persistent space and temporal space.

        file_name
            json file.
        """
        if _os.path.isfile(file_name):
            with open(file_name, "r") as file:
                loaded = _json.load(file)
                self.merge(loaded)

    def save(self, file_name : str):
        """
        Saves only values from persistent space.

        file_name
            json file.
        """
        with open(file_name, "w") as file:
            file.write(_json.dumps(self._persistent, indent = 4))

    def set_val(
            self, 
            full_name               : str, 
            value                   : ValueType, 
            value_type              : Type | None   = None, 
            *, 
            is_into_temporal_only   : bool          = False
                ):
        """
        full_name
            Name of namespaced value.
            For Example: "ui.box.size".
            If value do not exist, then will be created.
        value_type
            One of following types: bool, int, float, str, dict, list, None  
            If None, then does not convert value to value_type.
            Also makes sure that value is deep copied if mutable.
        is_into_temporal_only
            True  - Sets value in temporal space only.
            False - Sets value in both temporal space and persistent space.

        Raises
            TypeError - When value have unexpected type.
        """
        names = full_name.split(".")

        _set_val(self._temporal, names, value, value_type)
        if not is_into_temporal_only:
            _set_val(self._persistent, names, value, value_type)

    def set_int(self, full_name : str, value : int, *, is_into_temporal_only: bool = False):
        self.set_val(full_name, value, int, is_into_temporal_only = is_into_temporal_only) 

    def set_float(self, full_name : str, value : float, *, is_into_temporal_only: bool = False):
        self.set_val(full_name, value, float, is_into_temporal_only = is_into_temporal_only)

    def set_bool(self, full_name : str, value : bool, *, is_into_temporal_only: bool = False):
        self.set_val(full_name, value, bool, is_into_temporal_only = is_into_temporal_only)

    def set_str(self, full_name : str, value : str, *, is_into_temporal_only: bool = False):
        self.set_val(full_name, value, str, is_into_temporal_only = is_into_temporal_only)

    def set_dict(self, full_name : str, value : dict, *, is_into_temporal_only: bool = False):
        self.set_val(full_name, value, dict, is_into_temporal_only = is_into_temporal_only)

    def set_list(self, full_name : str, value : list, *, is_into_temporal_only: bool = False):
        self.set_val(full_name, value, list, is_into_temporal_only = is_into_temporal_only)
            
    def set_tmp_val(
            self, 
            full_name   : str, 
            value       : ValueType, 
            value_type  : Type | None   = None, 
                ):
        """
        Sets value in temporal space only.

        full_name
            Name of namespaced value.
            For Example: "ui.box.size".
            If value do not exist, then will be created.
        value_type
            One of following types: bool, int, float, str, dict, list, None  
            If None, then does not convert value to value_type.
            Also makes sure that value is deep copied if mutable.

        Raises
            TypeError - When value have unexpected type.
        """
        self.set_val(full_name, value, value_type, is_into_temporal_only = True)

    def set_tmp_int(self, full_name : str, value : int):
        self.set_tmp_val(full_name, value, int)

    def set_tmp_float(self, full_name : str, value : float):
        self.set_tmp_val(full_name, value, float)

    def set_tmp_bool(self, full_name : str, value : bool):
        self.set_tmp_val(full_name, value, bool)

    def set_tmp_str(self, full_name : str, value : str):
        self.set_tmp_val(full_name, value, str)

    def set_tmp_dict(self, full_name : str, value : dict):
        self.set_tmp_val(full_name, value, dict)

    def set_tmp_list(self, full_name : str, value : list):
        self.set_tmp_val(full_name, value, list)

    def get_val(
            self, 
            full_name           : str, 
            value_type          : Type | None   = None, 
            *, 
            is_from_temporal    : bool          = True
                ) -> ValueType:
        """
        full_name
            Name of namespaced value.
            For Example: "ui.box.size".
        value_type
            One of following types: bool, int, float, str, dict, list, None  
            If None, then does not convert value to value_type.
            Also makes sure that value is deep copied if mutable.
        is_from_temporal
            True    - Gets value from temporal space.
            False   - Gets value from persistent space.

        Dictionary is deep copied when returned.

        Raises
            KeyError - When value is not found.
        """
        names = full_name.split(".")

        if is_from_temporal:
            try:
                return _get_val(self._temporal, names, value_type)
            except KeyError as exception:
                raise KeyError(full_name) from exception
    
        else:
            try:
                return _get_val(self._persistent, names, value_type)
            except KeyError as exception:
                raise KeyError(full_name) from exception  
            
    def get_int(self, full_name : str, *, is_from_temporal : bool = True) -> int:
        return self.get_val(full_name, int, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def get_float(self, full_name : str, *, is_from_temporal : bool = True) -> float:
        return self.get_val(full_name, float, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def get_bool(self, full_name : str, *, is_from_temporal : bool = True) -> bool:
        return self.get_val(full_name, bool, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def get_str(self, full_name : str, *, is_from_temporal : bool = True) -> str:
        return self.get_val(full_name, str, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def get_dict(self, full_name : str, *, is_from_temporal : bool = True) -> dict:
        return self.get_val(full_name, dict, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def get_list(self, full_name : str, *, is_from_temporal : bool = True) -> list:
        return self.get_val(full_name, list, is_from_temporal = is_from_temporal) # type: ignore[return-value]
            
    def try_get_val(
            self, 
            full_name           : str, 
            value_type          : Type | None   = None, 
            *, 
            is_from_temporal    : bool          = True
                ) -> ValueType | None:
        """
        full_name
            Name of namespaced value.
            For Example: "ui.box.size".
        value_type
            One of following types: bool, int, float, str, dict, list, None  
            If None, then does not convert value to value_type.
            Also makes sure that value is deep copied if mutable.
        is_from_temporal
            True    - Gets value from temporal space.
            False   - Gets value from persistent space.
        Returns
            value   - When value is found.
            None    - Otherwise.
        """
        try:
            return self.get_val(full_name, value_type, is_from_temporal = is_from_temporal)
        except KeyError:
            return None
        
    def try_get_int(self, full_name : str, *, is_from_temporal : bool = True) -> int:
        return self.try_get_val(full_name, int, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def try_get_float(self, full_name : str, *, is_from_temporal : bool = True) -> float:
        return self.try_get_val(full_name, float, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def try_get_bool(self, full_name : str, *, is_from_temporal : bool = True) -> bool:
        return self.try_get_val(full_name, bool, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def try_get_str(self, full_name : str, *, is_from_temporal : bool = True) -> str:
        return self.try_get_val(full_name, str, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def try_get_dict(self, full_name : str, *, is_from_temporal : bool = True) -> dict:
        return self.try_get_val(full_name, dict, is_from_temporal = is_from_temporal) # type: ignore[return-value]
    
    def try_get_list(self, full_name : str, *, is_from_temporal : bool = True) -> list:
        return self.try_get_val(full_name, list, is_from_temporal = is_from_temporal) # type: ignore[return-value]
        
    def copy_val(
            self, 
            full_name_from          : str, 
            full_name_to            : str, 
            *, 
            is_from_temporal        : bool      = True, 
            is_into_temporal_only   : bool      = False
                ):
        """
        Copy value.
        
        is_from_temporal
            True    - Gets value from temporal space.
            False   - Gets value from persistent space.
        is_into_temporal_only
            True    - Sets value in temporal space only.
            False   - Sets value in both temporal space and persistent space.  

        Raises
            KeyError - When value is not found.
        """
        val = self.get_val(full_name_from, is_from_temporal = is_from_temporal)
        self.set_val(full_name_to, val, is_into_temporal_only = is_into_temporal_only)

    def copy_tmp_val(self, full_name_from : str, full_name_to : str):
        """
        Copies temporal value to temporals, or renames temporal value. 
        Type of of value is preserved.

        Raises
            KeyError - When value is not found.
        """
        val = self.get_val(full_name_from, is_from_temporal = True)
        self.set_tmp_val(full_name_to, val)
        
    def merge(self, external : dict[str, ValueType], *, is_into_temporal_only : bool = False):
        """
        Merges with external settings.

        is_into_temporal_only
            True    - Merges into temporal space only.
            False   - Merges into both temporal space and persistent space. 
        """
        if not is_into_temporal_only:
            self._persistent = _deepcopy(_merge_on_all_levels(self._persistent, external))
        self._temporal = _deepcopy(_merge_on_all_levels(self._temporal, external))

    def to_persistent(self):
        return self._persistent
    
    def to_temporal(self):
        return self._temporal


def _set_val(
        settings    : dict[str, ValueType], 
        names       : list[str], 
        value       : ValueType, 
        value_type  : Type | None               = None
            ):
    if not isinstance(value, (bool, int, float, str, list, dict)): # assumes that dictionaries are ValueType on all levels
        raise TypeError("Parameter 'value' have unexpected type.")

    level = settings
    for name in names[:-1]:
        if name not in level:
            level[name] = {}
        level = level[name] # type: ignore[assignment] 

    if isinstance(value, (dict, list)):
        value = _deepcopy(value)

    if value_type is None or isinstance(value, value_type):
        level[names[-1]] = value
    else:
        level[names[-1]] = value_type(value)


def _get_val(
        settings    : dict[str, ValueType], 
        names       : list[str], 
        value_type  : Type | None               = None
            ) -> ValueType:
    level = settings
    for name in names[:-1]:
        level = level[name] # type: ignore[assignment] 

    value = level[names[-1]]
    if isinstance(value, (dict, list)):
        value = _deepcopy(value)

    if value_type is None or isinstance(value, value_type):
        return value
    return value_type(value)