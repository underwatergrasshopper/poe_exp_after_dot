# 0.1.4 (2024-02-02)
* Added debug for text reading.
* Added more debug logging for fetching current exp value.
* Added usage of `faulthandler` for reading in-game exp tooltip in debug mode.
* Changed Error Board hints to be more informative.
* Changed key controls for Error Board.
* Changed error message format, when incorrect command option is put, to be more strict.
* Fixed temporal displacement in debug mode.
* Fixed bug where python would crash when overlay trying do measurement after LMB click on exp bar.
# 0.1.3 (2024-01-31)
* Added logging monitor resolution to `runtime.log`.
* Added highlighting of in-game exp tooltip region for debug mode.
* Added ability to create run script on desktop by using option `--make-run-file`.
* Updated README.md.
* Removed creating run script at installation.
* Fixed incorrect offset between mouse cursor and in-game exp tooltip.
* Fixed bug where debug mode can not be fully disabled.
# 0.1.2 (2024-01-21)
* Removed wrongly defined `__repr__` implementations.
# 0.1.1 (2024-01-09)
* Added displaying version information.
* Updated date in LICENSE.
* Removed information from README.md, about installing through pip database, since it is not there yet.
# 0.1.0
* Added ability to run `poe_exp_after_dot_tests` from package level.
* Refactored `Run{...}.bat` functions to be more direct.
* Changed color of integer part of progress step in InfoBoard.
* Improved measurement stability.
* Fixed typos.
