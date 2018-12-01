# coding: utf8
from __future__ import unicode_literals

import sys
from pathlib import Path

from .json import ujson


def read_json(location):
    """Open and load JSON from file.

    location (Path): The file path. "-" for reading from stdin.
    RETURNS (dict): Loaded JSON content.
    """
    if location == "-":  # reading from sys.stdin
        data = sys.stdin.read()
        return ujson.loads(data)
    file_path = _force_path(location)
    with file_path.open("r", encoding="utf8") as f:
        return ujson.load(f)


def write_json(location, contents, indent=2):
    """Create a .json file and dump contents.

    location (unicode / Path): The file path. "-" for writing to stdout.
    contents: The JSON-serializable contents to output.
    indent (int): Number of spaces used to indent JSON.
    """
    data = _json_dumps(contents, indent=indent)
    if location == "-":  # writing to stdout
        print(data)
        return
    file_path = _force_path(location)
    with file_path.open("w", encoding="utf8") as f:
        f.write(data)


def read_jsonl(location, skip=False):
    """Read a .jsonl file and yield its contents line by line.

    location (unicode / Path): The file path. "-" for reading from stdin.
    skip (bool): Skip broken lines and don't raise ValueError.
    YIELDS: The loaded JSON contents of each line.
    """
    if location == "-":  # reading from sys.stdin
        for line in _yield_json_lines(sys.stdin, skip=skip):
            yield line
    file_path = _force_path(location)
    with file_path.open("r", encoding="utf8") as f:
        for line in _yield_json_lines(f, skip=skip):
            yield line


def write_jsonl(location, lines):
    """Create a .jsonl file and dump contents.

    location (unicode / Path): The file path. "-" for writing to stdout.
    lines (list): The JSON-serializable contents of each line.
    """
    if location == "-":  # writing to stdout
        for line in lines:
            print(_json_dumps(line))
    else:
        file_path = _force_path(location)
        with file_path.open("a", encoding="utf-8") as f:
            for line in lines:
                f.write(_json_dumps(line) + "\n")


def is_json_serializable(obj):
    """Check if a Python object is JSON-serializable."""
    if hasattr(obj, "__call__"):
        # Check this separately here to prevent infinite recursions
        return False
    try:
        ujson.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def _yield_json_lines(stream, skip=False):
    line_no = 1
    for line in stream:
        line = line.strip()
        try:
            yield ujson.loads(line)
        except ValueError:
            if line == "" or skip:
                continue
            raise ValueError("Invalid JSON on line {}: {}".format(line_no, line))
        line_no += 1


def _force_path(location):
    file_path = Path(location)
    if not file_path.exists():
        raise ValueError("Can't read file: {}".format(location))
    return file_path


def _json_dumps(data, indent=0):
    result = ujson.dumps(data, indent=indent, escape_forward_slashes=False)
    if sys.version_info[0] == 2:  # Python 2
        return result.decode("utf8")
    return result
