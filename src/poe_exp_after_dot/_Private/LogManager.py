import os       as _os
import sys      as _sys

import logging


class LogManager:
    _logger         : logging.Logger
    _file_handler   : logging.FileHandler | None
    _log_file_name  : str | None

    def __init__(self, logger_name : str):
        self._logger        = logging.getLogger(logger_name)
        self._file_handler  = None
        self._log_file_name = None

    def setup_logger(self, log_file_name : str | None = None, *, is_debug : bool = False, is_stdout : bool = False):
        formatter = logging.Formatter(fmt = "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")

        if is_stdout:
            stream_handler = logging.StreamHandler(_sys.stdout)
            stream_handler.setFormatter(formatter)
            self._logger.addHandler(stream_handler)

        if log_file_name:
            path = _os.path.dirname(log_file_name)
            _os.makedirs(path, exist_ok = True)

            self._file_handler = logging.FileHandler(log_file_name, "a")
            self._file_handler.setFormatter(formatter)
            self._logger.addHandler(self._file_handler)

            self._log_file_name = log_file_name

        self._logger.setLevel(logging.DEBUG if is_debug else logging.INFO)

    def clear_log_file(self):
        if self._file_handler and self._log_file_name:
            formatter = self._file_handler.formatter
            self._file_handler.close()
            self._logger.removeHandler(self._file_handler)

            self._file_handler = logging.FileHandler(self._log_file_name, "w")
            self._file_handler.setFormatter(formatter)
            self._logger.addHandler(self._file_handler)

    def set_is_debug(self, is_debug = True):
        self._logger.setLevel(logging.DEBUG if is_debug else logging.INFO)

    def to_logger(self) -> logging.Logger:
        return self._logger
    

_log_manager = LogManager("poe_exp_after_dot")


def to_log_manager() -> LogManager:
    return _log_manager


def to_logger() -> logging.Logger:
    return to_log_manager().to_logger()
