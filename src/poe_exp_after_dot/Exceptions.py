class Error(Exception):
    pass

class TemplateLoadFail(Error):
    pass

class TextGenFail(Error):
    pass

class CommandArgumentError(Error):
    pass