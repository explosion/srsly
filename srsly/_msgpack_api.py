# coding: utf8
from __future__ import unicode_literals

import gc

from . import msgpack
from .util import force_path


def msgpack_dumps(data):
    return msgpack.dumps(data, use_bin_type=True)


def msgpack_loads(data):
    # msgpack-python docs suggest disabling gc before unpacking large messages
    gc.disable()
    msg = msgpack.loads(data, raw=False)
    gc.enable()
    return msg


def read_msgpack(location):
    file_path = force_path(location)
    with file_path.open("rb") as f:
        gc.disable()
        msg = msgpack.load(f, raw=False)
        gc.enable()
        return msg


def write_msgpack(location, data):
    file_path = force_path(location, require_exists=False)
    with file_path.open("wb") as f:
        msgpack.dump(data, f, use_bin_type=True)
