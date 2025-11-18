import gc
from contextlib import contextmanager

import msgpack

from .util import force_path, FilePath, JSONInputBin, JSONOutputBin
from ._msgpack_numpy import encode_numpy, decode_numpy


class _MsgpackExtensions:
    __slots__ = ("_ext",)

    def __init__(self):
        self._ext = {}

    def register(self, name, func):
        """Register a custom encoder/decoder function"""
        self._ext[name] = func

    def deregister(self, name):
        del self._ext[name]

    def _run(self, obj):
        for func in self._ext.values():
            out = func(obj)
            if out is not obj:
                return out

        # Convert subtypes of base types and tuples to lists.
        # Effectively this undoes the strict_types=True option of msgpack.
        # This is needed to support np.float64, which is a subclass of builtin float.
        # Run this last to allow the user to register their own handlers first.
        if isinstance(obj, tuple):
            return list(obj)
        # Note: bool and memoryview can't be subclassed
        # set and frozenset are not supported by msgpack
        for cls in (int, float, list, dict, str, bytes):
            if isinstance(obj, cls):
                return cls(obj)

        return obj


msgpack_encoders = _MsgpackExtensions()
msgpack_decoders = _MsgpackExtensions()


def encode_complex(obj):
    if isinstance(obj, complex):
        return {b"complex": True, b"data": repr(obj)}
    return obj


def decode_complex(obj):
    if b"complex" in obj:
        return complex(obj[b"data"])
    return obj


msgpack_encoders.register("numpy", func=encode_numpy)
msgpack_decoders.register("numpy", func=decode_numpy)
# Note: np.complex128 is a subclass of built-in complex, so
# encode_complex must be registered after encode_numpy.
msgpack_encoders.register("complex", func=encode_complex)
msgpack_decoders.register("complex", func=decode_complex)


@contextmanager
def _without_gc():
    """msgpack-python docs suggest disabling gc before unpacking large messages"""
    gc.disable()
    try:
        yield
    finally:
        gc.enable()


def msgpack_dumps(data: JSONInputBin) -> bytes:
    """Serialize an object to a msgpack byte string.

    data: The data to serialize.
    RETURNS (bytes): The serialized bytes.
    """
    return msgpack.dumps(
        data,
        # strict_types is False for everything except np.float64
        # and np.complex128 (see above)
        strict_types=True,
        default=msgpack_encoders._run,
    )


def msgpack_loads(data: bytes, use_list: bool = True) -> JSONOutputBin:
    """Deserialize msgpack bytes to a Python object.

    data (bytes): The data to deserialize.
    use_list (bool): Don't use tuples instead of lists. Can make
        deserialization slower.
    RETURNS: The deserialized Python object.
    """
    with _without_gc():
        return msgpack.loads(
            data, raw=False, use_list=use_list, object_hook=msgpack_decoders._run
        )


def write_msgpack(path: FilePath, data: JSONInputBin) -> None:
    """Create a msgpack file and dump contents.

    location (FilePath): The file path.
    data (JSONInputBin): The data to serialize.
    """
    file_path = force_path(path, require_exists=False)
    with file_path.open("wb") as f:
        msgpack.dump(data, f, strict_types=True, default=msgpack_encoders._run)


def read_msgpack(path: FilePath, use_list: bool = True) -> JSONOutputBin:
    """Load a msgpack file.

    location (FilePath): The file path.
    use_list (bool): Don't use tuples instead of lists. Can make
        deserialization slower.
    RETURNS (JSONOutputBin): The loaded and deserialized content.
    """
    file_path = force_path(path)
    with file_path.open("rb") as f, _without_gc():
        return msgpack.load(
            f, raw=False, use_list=use_list, object_hook=msgpack_decoders._run
        )
