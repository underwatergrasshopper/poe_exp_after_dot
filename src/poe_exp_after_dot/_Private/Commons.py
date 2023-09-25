EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def pad_to_length(text : str, length : int):
        """
        If 'text' is shorter than 'length', then adds padding to front of 'text', until length of text is equal to 'length'.
        If 'text' is longer than 'length', then shorts 'text', until length of text is equal to 'length'.
        """
        return text.rjust(length)[:length]