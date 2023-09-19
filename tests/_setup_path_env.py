"""
This module is only for internal use. Do not import or run it.
"""
import os   as _os
import sys  as _sys

_base_path = _os.path.dirname(__file__)

def _make_full_path(rel_path : str) -> str:
    full_path = _base_path
    if len(rel_path) > 0:
        full_path += "/" + rel_path

    return _os.path.abspath(full_path)

def _exclude_from_path(rel_paths : list[str]):
    for rel_path in rel_paths:
        full_path = _make_full_path(rel_path)
        try:
            _sys.path.remove(full_path)
        except ValueError:
            pass

def _prepend_path(rel_paths : list[str]):
    _exclude_from_path(rel_paths)

    rel_paths.reverse()
    for rel_path in rel_paths:
        _sys.path.insert(0, _make_full_path(rel_path))

def run():
    """
    Adds necessary paths to path environment variable.
    """
    _exclude_from_path([
        "..",
    ])

    _prepend_path([
        "../src",
        "",
    ])
