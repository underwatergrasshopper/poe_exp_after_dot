import os

from typing import SupportsFloat, SupportsInt, Sequence, Any
from dataclasses import dataclass

NONE_NAME = "[None]"

class Character:
    _name                   : str
    _data_path              : str

    _character_folder_path  : str | None
    _exp_data_file_name     : str

    def __init__(self, name : str, data_path : str):
        """
        name 
            Name of character or NONE_NAME.
        """
        self._name                  = name
        self._data_path             = data_path

        if name != NONE_NAME:
            self._character_folder_path     = os.path.abspath(data_path) + "/characters/" + name
            self._exp_data_file_name        = self._character_folder_path + "/exp_data.json"
        else:
            self._character_folder_path     = None
            self._exp_data_file_name        = os.path.abspath(data_path) + "/exp_data.json"

        self._create()

    def get_name(self) -> str:
        return self._name
    
    def get_exp_data_file_name(self) -> str:
        return self._exp_data_file_name

    def _create(self):
        if self._character_folder_path is not None:
            os.makedirs(self._character_folder_path, exist_ok = True)

        if not os.path.exists(self._exp_data_file_name):
            with open(self._exp_data_file_name, "w") as file:
                file.write("[]")

    def destroy(self):
        if os.path.isfile(self._exp_data_file_name):
            os.remove(self._exp_data_file_name)

        # to make sure it's a correct folder
        if self._character_folder_path is not None and "characters" in self._character_folder_path and len(os.listdir(self._character_folder_path)) == 0:
            os.rmdir(self._character_folder_path)

class CharacterRegister:
    _data_path : str
    _characters : dict[str, Character]

    def __init__(self, data_path : str):
        self._data_path = os.path.abspath(data_path)
        self._characters = {}

    def scan_for_characters(self):
        characters_path = self._data_path + "/characters"

        if os.path.exists(characters_path):
            for name in os.listdir(characters_path):
                if os.path.isdir(characters_path + "/" + name):
                    self.create_character(name)

    def create_character(self, name : str):
        if name == "":
            name = NONE_NAME

        character = Character(name, self._data_path)
        self._characters[name] = character
        return character

    def destroy_character(self, name : str):
        if name == "":
            name = NONE_NAME
            
        self._characters[name].destroy()
        del self._characters[name]

    def to_character(self, name) -> Character:
        if name == "":
            name = NONE_NAME

        if name not in self._characters:
            self.create_character(name)

        return self._characters[name]
    
    def get_character_names(self, *, is_include_none_name = False) -> list[str]:
        if is_include_none_name:
            return [name for name in self._characters.keys()]
        else:
            return [name for name in self._characters.keys() if name != NONE_NAME]