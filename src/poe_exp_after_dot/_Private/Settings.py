import os
import json

from typing import Any
from copy import deepcopy as _deepcopy

from .Commons import merge_on_all_levels as _merge_on_all_levels

class Settings:
    _file_name  : str
    _default    : dict[str, Any]
    _temporal   : dict[str, Any]
    _settings   : dict[str, Any]

    def __init__(self, file_name : str, default : dict[str, Any]):
        self._file_name = file_name
        self._default   = default
        self._temporal  = {}
        self._settings  = {}

    def load_and_add_temporal(self, temporal : dict[str, Any]):
        if os.path.isfile(self._file_name):
            with open(self._file_name, "r") as file:
                self._settings = json.load(file)
        else:
            with open(self._file_name, "w") as file:
                file.write(json.dumps(self._default, indent = 4))

        self._settings = _deepcopy(_merge_on_all_levels(self._default, self._settings))
        self._temporal = _deepcopy(_merge_on_all_levels(self._settings, temporal))

    def set_val(self, full_name : str, value, value_type : type, *, is_temporal_only : bool = False):
        """
        full_name
            Names of levels and variable separated by '.'. 
            For Example: "ui.box.size".
            If value with levels do not exist, then will be created.
        """
        names = full_name.split(".")

        try:
            self._set_val(self._temporal, names, value, value_type)
        except Exception as exception:
            raise RuntimeError(f"Can not assigns value to temporal settings with name path \"{full_name}\".") from exception

        if not is_temporal_only:
            try:
                self._set_val(self._settings, names, value, value_type)
            except Exception as exception:
                raise RuntimeError(f"Can not assigns value to settings with name path \"{full_name}\".") from exception

    def get_val(self, full_name : str, value_type : type = object, *, is_temporal : bool = True) -> Any:
        """
        full_name
            Names of levels and variable separated by '.'. 
            For Example: "ui.box.size".
        """
        names = full_name.split(".")

        if is_temporal:
            try:
                return self._get_val(self._temporal, names, value_type)
            except Exception as exception:
                raise RuntimeError(f"Can not get value from temporal settings with full name \"{full_name}\".") from exception
    
        else:
            try:
                return self._get_val(self._settings, names, value_type)
            except Exception as exception:
                raise RuntimeError(f"Can not get value from settings with full name \"{full_name}\".") from exception
            
    def try_get_val(self, full_name : str, value_type : type = object, *, is_temporal : bool = True) -> Any | None:
        """
        full_name
            Names of levels and variable separated by '.'. 
            For Example: "ui.box.size".
        """
        try:
            return self.get_val(full_name, value_type, is_temporal = is_temporal)
        except RuntimeError:
            return None

    def save(self):
        with open(self._file_name, "w") as file:
            file.write(json.dumps(self._settings, indent = 4))

    def _set_val(self, settings : dict[str, Any], names : list[str], value, value_type : type):
        level = settings
        for name in names[:-1]:
            if name not in level:
                level[name] = {}
            level = level[name]
        level[names[-1]] = value_type(value)

    def _get_val(self, settings : dict[str, Any], names : list[str], value_type : type) -> Any:
        level = settings
        for name in names[:-1]:
            if name not in level:
                level[name] = {}
            level = level[name]
        if value_type == object:
            return level[names[-1]]
        return value_type(level[names[-1]])