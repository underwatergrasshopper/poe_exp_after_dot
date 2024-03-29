# 0.2.0 (2024-03-25)
* Added ability to run tests in specific order.
* Changed required python version to be 3.11 only.
* Changed stream indicator of error messages to be `stderr` for all error print outs.
* Changed interface of ErrorBoard. Refactored handling of command line arguments.
* Changed displaying error details in ErrorBoard. Now it requires `--error-details` option to be available.
* Changed displaying command line argument errors. Now it doesn't display trace in code.
* Changed paths to files and folder to have same format. Windows format with `single backslash` as separator.
* Changed project scripts. Project scripts now can be called from other directory than project directory.
* Changed logging behaviour to: log errors and critical errors to `stderr` and other messages to `stdout`, instead just to `stdout`. Logging to file is still present.
# 0.1.5 (2024-02-05)
* Added more common thousands separators to text scan format of current exp value.
* Added information about required "Path of Exile" language to README.md.
* Fixed missing output stream for logger, while trying to log in debug mode, when scanning text.
# 0.1.4 (2024-02-02)
* Added debug for text reading.
* Added more debug logging for fetching current exp value.
* Added usage of `faulthandler` for reading in-game exp tooltip in debug mode.
* Changed Error Board hints to be more informative.
* Changed key controls for Error Board.
* Changed error message format, when incorrect command option is put, to be more strict.
* Fixed temporal displacement in debug mode.
* Fixed bug where python would crash when overlay trying do measurement after LMB click on exp bar.
* Fixed crash when trying do measure when debug mode is enabled and overlay is executed by `start pyw ...`.
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
