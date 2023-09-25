from typing import Any

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def pad_to_length(text : str, length : int):
        """
        If 'text' is shorter than 'length', then adds padding to front of 'text', until length of text is equal to 'length'.
        If 'text' is longer than 'length', then shorts 'text', until length of text is equal to 'length'.
        """
        return text.rjust(length)[:length]

def try_get(settings : dict[str | Any], name : str, value_type : type) -> int:
    return value_type(settings.get(name))