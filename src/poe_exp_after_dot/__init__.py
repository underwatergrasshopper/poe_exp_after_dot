
from ._Private.Overlay import Overlay as _Overlay

def _main(argv : list[str]) -> int:
    overlay = _Overlay()
    return overlay.main(argv)

if __name__ == "__main__":
    import sys as _sys
    
    exit_code = _main(_sys.argv)
    _sys.exit(exit_code)