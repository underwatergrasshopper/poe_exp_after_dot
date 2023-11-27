import os   as _os
import json as _json

from typing import Any, Type
from copy   import deepcopy as _deepcopy

from .Commons import merge_on_all_levels as _merge_on_all_levels

class Settings:
    """
    <name>
        (<namespace>\\.)*<variable_name>
        
    <namespace>
        <level_name>(\\.<level_name>)*
    """
    _persistent         : dict[str, Any]
    _temporal           : dict[str, Any]

    def __init__(self):
        self._temporal  = {}
        self._persistent  = {}
        
    def load(self, file_name : str):
        if _os.path.isfile(file_name):
            with open(file_name, "r") as file:
                loaded = _json.load(file)

                self._persistent    = _deepcopy(_merge_on_all_levels(self._persistent, loaded))
                self._temporal      = _deepcopy(_merge_on_all_levels(self._temporal, loaded))

    def save(self, file_name : str):
        with open(file_name, "w") as file:
            file.write(_json.dumps(self._persistent, indent = 4))

    def set_val(self, full_name : str, value, value_type : Type = str, *, is_into_temporal_only : bool = False):
        """
        name
            Name containing names of levels and variable separated by '.'. 
            For Example: "ui.box.size".
            If value with levels do not exist, then will be created.
        """
        names = full_name.split(".")

        try:
            _set_val(self._temporal, names, value, value_type)
        except Exception as exception:
            raise RuntimeError(f"Can not assigns value to temporal settings with name path \"{full_name}\".") from exception

        if not is_into_temporal_only:
            try:
                _set_val(self._persistent, names, value, value_type)
            except Exception as exception:
                full_name = ".".join(names)
                raise RuntimeError(f"Can not assigns value to settings with name path \"{full_name}\".") from exception

    def get_val(self, full_name : str, value_type : Type = str, *, is_from_temporal : bool = True) -> Any:
        """
        full_name
            Name containing names of levels and variable separated by '.'. 
            For Example: "ui.box.size".
        """
        names = full_name.split(".")

        if is_from_temporal:
            try:
                return _get_val(self._temporal, names, value_type)
            except Exception as exception:
                raise RuntimeError(f"Can not get value from temporal settings with full name \"{full_name}\".") from exception
    
        else:
            try:
                return _get_val(self._persistent, names, value_type)
            except Exception as exception:
                raise RuntimeError(f"Can not get value from settings with full name \"{full_name}\".") from exception
            
    def try_get_val(self, full_name : str, value_type : Type = str, *, is_temporal : bool = True) -> Any | None:
        """
        full_name
            Name containing names of levels and variable separated by '.'. 
            For Example: "ui.box.size".
        """
        try:
            return self.get_val(full_name, value_type, is_from_temporal = is_temporal)
        except RuntimeError:
            return None
        
    def merge_with(self, settings : dict[str, Any], *, is_into_temporal_only : bool = False):
        if not is_into_temporal_only:
            self._persistent = _deepcopy(_merge_on_all_levels(self._persistent, settings))
        self._temporal = _deepcopy(_merge_on_all_levels(self._temporal, settings))

    def to_persistent(self):
        return self._persistent
    
    def to_temporal(self):
        return self._temporal


def _set_val(settings : dict[str, Any], names : list[str], value, value_type : Type):
    level = settings
    for name in names[:-1]:
        if name not in level:
            level[name] = {}
        level = level[name]
    level[names[-1]] = value_type(value)

def _get_val(settings : dict[str, Any], names : list[str], value_type : Type) -> Any:
    level = settings
    for name in names[:-1]:
        if name not in level:
            level[name] = {}
        level = level[name]
    if value_type == object:
        return level[names[-1]]
    return value_type(level[names[-1]])