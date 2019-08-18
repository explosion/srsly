# coding: utf8
from __future__ import unicode_literals

from pathlib import Path
import sys


is_python2 = sys.version_info[0] == 2
is_python3 = sys.version_info[0] == 3

if is_python2:
    basestring_ = basestring  # noqa: F821
else:
    basestring_ = str


def force_path(location, require_exists=True):
    if not isinstance(location, Path):
        location = Path(location)
    if require_exists and not location.exists():
        raise ValueError("Can't read file: {}".format(location))
    return location


def force_string(location):
    if isinstance(location, basestring_):
        return location
    if sys.version_info[0] == 2:  # Python 2
        return str(location).decode("utf8")
    return str(location)
