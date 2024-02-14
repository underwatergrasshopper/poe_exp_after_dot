def _execute():
    import sys
    from . import _main

    sys.exit(_main(sys.argv))

_execute()