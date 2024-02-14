import os as _os

from .LogManager    import to_logger
from .Commons       import character_name_to_log_name

class Character:
    _name                   : str
    _data_path              : str

    _character_folder_path  : str | None
    _exp_data_file_name     : str

    def __init__(self, name : str, data_path : str):
        """
        name 
            Name of character or empty string.
        """
        self._name                  = name
        self._data_path             = data_path

        if name == "":
            self._character_folder_path     = None
            self._exp_data_file_name        = _os.path.abspath(data_path) + "\\exp_data.json"
        else:
            self._character_folder_path     = _os.path.abspath(data_path) + "\\characters\\" + name
            self._exp_data_file_name        = self._character_folder_path + "\\exp_data.json"

        self._create()

    def get_name(self) -> str:
        return self._name
    
    def get_exp_data_file_name(self) -> str:
        return self._exp_data_file_name

    def _create(self):
        if self._character_folder_path is not None:
            _os.makedirs(self._character_folder_path, exist_ok = True)

        if not _os.path.exists(self._exp_data_file_name):
            with open(self._exp_data_file_name, "w") as file:
                file.write("[]")

    def destroy(self):
        if _os.path.isfile(self._exp_data_file_name):
            _os.remove(self._exp_data_file_name)

        # to make sure it's a correct folder
        if self._character_folder_path is not None and "characters" in self._character_folder_path and len(_os.listdir(self._character_folder_path)) == 0:
            _os.rmdir(self._character_folder_path)

class CharacterRegister:
    _data_path : str
    _characters : dict[str, Character]

    def __init__(self, data_path : str):
        self._data_path = _os.path.abspath(data_path)
        self._characters = {}

    def scan_for_characters(self):
        characters_path = self._data_path + "\\characters"

        if _os.path.exists(characters_path):
            for name in _os.listdir(characters_path):
                if _os.path.isdir(characters_path + "\\" + name):
                    self.add_character(name)

    def add_character(self, name : str):
        """
        Does not overwrites character data files in 'characters' folder.
        Creates new files if they do not exist.

        name
            Name of character. Can be an empty string. 
            If empty string, then is identified as generic character.
            Generic character is without name.
        """
        character = Character(name, self._data_path)
        self._characters[name] = character

        to_logger().info(f"Registered character data for {character_name_to_log_name(name)}. (Creates file structure if doesn't exist.)")

        return character

    def destroy_character(self, name : str):
        self._characters[name].destroy()
        del self._characters[name]

        to_logger().info(f"Destroyed character data for {character_name_to_log_name(name)}.")

    def to_character(self, name) -> Character:
        if name not in self._characters:
            self.add_character(name)

        return self._characters[name]
    
    def get_character_names(self, *, is_include_empty_name = False) -> list[str]:
        if is_include_empty_name:
            return [name for name in self._characters.keys()]
        else:
            return [name for name in self._characters.keys() if name != ""]