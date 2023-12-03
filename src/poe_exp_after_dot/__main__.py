def _execute():
    import sys
    from . import main

    sys.exit(main(sys.argv))


_execute()