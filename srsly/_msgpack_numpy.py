"""
Support for serialization of numpy data types with msgpack.
This is a heavily modified fork of a very old version of msgpack-numpy.
"""

# Copyright (c) 2013-2018, Lev E. Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license
try:
    import numpy as np

    has_numpy = True
except ImportError:
    has_numpy = False

try:
    import cupy

    has_cupy = True
except ImportError:
    has_cupy = False


def encode_numpy(obj):
    """
    Data encoder for serializing numpy data types.
    """
    if not has_numpy:
        return obj
    if has_cupy and isinstance(obj, cupy.ndarray):
        obj = obj.get()
    if isinstance(obj, np.ndarray):
        # If the dtype is structured, store the interface description;
        # otherwise, store the corresponding array protocol type string:
        if obj.dtype.kind == "V":
            kind = b"V"
            descr = obj.dtype.descr
        else:
            kind = b""
            descr = obj.dtype.str
        return {
            b"nd": True,
            b"type": descr,
            b"kind": kind,
            b"shape": obj.shape,
            b"data": obj.data if obj.flags["C_CONTIGUOUS"] else obj.tobytes(),
        }
    if isinstance(obj, (np.bool_, np.number)):
        return {b"nd": False, b"type": obj.dtype.str, b"data": obj.data}

    return obj


def decode_numpy(obj):
    """
    Decoder for deserializing numpy data types.
    """
    if b"nd" not in obj:
        return obj

    # Crash with a clean ModuleNotFoundError if numpy is not available
    # instead of AttributeError
    import numpy  # noqa: F401

    if obj[b"nd"]:
        # Check if "kind" is in obj to enable decoding of data
        # serialized with older versions (#20):
        if b"kind" in obj and obj[b"kind"] == b"V":
            descr = [
                tuple(t.decode() if type(t) is bytes else t for t in d)
                for d in obj[b"type"]
            ]
        else:
            descr = obj[b"type"]
        return np.frombuffer(obj[b"data"], dtype=np.dtype(descr)).reshape(obj[b"shape"])
    else:
        # NumPy scalar
        descr = obj[b"type"]
        return np.frombuffer(obj[b"data"], dtype=np.dtype(descr))[0]
