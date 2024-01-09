_version : str = ""

def set_version(version : str):
    global _version
    _version = version

def get_version() -> str:
    return _version