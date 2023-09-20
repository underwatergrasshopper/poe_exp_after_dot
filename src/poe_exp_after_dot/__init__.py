
from ._Private.Overlay import Overlay as _Overlay

def _main(argv : list[str]):
    overlay = _Overlay()
    overlay.main(argv)

if __name__ == "__main__":
    import sys as _sys
    
    _main(_sys.argv)