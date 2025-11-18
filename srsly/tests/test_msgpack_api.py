import datetime
from collections import namedtuple
from pathlib import Path

import pytest

from .._msgpack_api import read_msgpack, write_msgpack
from .._msgpack_api import msgpack_loads, msgpack_dumps
from .._msgpack_api import msgpack_encoders, msgpack_decoders
from .util import make_tempdir


def test_msgpack_dumps():
    data = {"hello": "world", "test": 123}
    expected = [b"\x82\xa5hello\xa5world\xa4test{", b"\x82\xa4test{\xa5hello\xa5world"]
    msg = msgpack_dumps(data)
    assert msg in expected


def test_msgpack_loads():
    msg = b"\x82\xa5hello\xa5world\xa4test{"
    data = msgpack_loads(msg)
    assert len(data) == 2
    assert data["hello"] == "world"
    assert data["test"] == 123


def test_read_msgpack_file():
    file_contents = b"\x81\xa5hello\xa5world"
    with make_tempdir({"tmp.msg": file_contents}, mode="wb") as temp_dir:
        file_path = temp_dir / "tmp.msg"
        assert file_path.exists()
        data = read_msgpack(file_path)
    assert len(data) == 1
    assert data["hello"] == "world"


def test_read_msgpack_file_invalid():
    file_contents = b"\xa5hello\xa5world"
    with make_tempdir({"tmp.msg": file_contents}, mode="wb") as temp_dir:
        file_path = temp_dir / "tmp.msg"
        assert file_path.exists()
        with pytest.raises(ValueError):
            read_msgpack(file_path)


def test_write_msgpack_file():
    data = {"hello": "world", "test": 123}
    expected = [b"\x82\xa5hello\xa5world\xa4test{", b"\x82\xa4test{\xa5hello\xa5world"]
    with make_tempdir(mode="wb") as temp_dir:
        file_path = temp_dir / "tmp.msg"
        write_msgpack(file_path, data)
        with Path(file_path).open("rb") as f:
            assert f.read() in expected


def test_msgpack_complex():
    inp = {"a": 1 + 2j}
    out = msgpack_loads(msgpack_dumps(inp))
    assert out == inp
    # Test that we didn't accidentally convert to np.complex128,
    # which is a subclass of complex
    assert type(out["a"]) is complex


def test_msgpack_unknown_types():
    """Test that msgpack raises correct errors (e.g. when serializing
    datetime objects, the error should be msgpack's TypeError,
    not a "'np' is not defined error").
    """
    with pytest.raises(TypeError, match="datetime.datetime"):
        msgpack_dumps(datetime.datetime.now())


@pytest.mark.parametrize(
    "base_cls,data",
    [
        (int, 1),
        (float, 1),
        (list, [1, 2]),
        (dict, {"x": 1}),
        (str, "foo"),
        (bytes, b"foo"),
    ],
)
def test_msgpack_subtypes(base_cls, data):
    """Subtypes of base types are cast to their parents."""

    class SubType(base_cls):
        pass

    inp = SubType(data)
    out = msgpack_loads(msgpack_dumps(inp))
    assert type(out) is base_cls
    assert out == base_cls(data)


def test_msgpack_tuple():
    # There is no difference between list and tuple in msgpack
    # Outcome is controlled by the use_list=True parameter
    class MyTuple(tuple):
        pass

    Named = namedtuple("Named", ["x", "y", "z"])

    b1 = msgpack_dumps((1, 2, 3))
    b2 = msgpack_dumps([1, 2, 3])
    b3 = msgpack_dumps(MyTuple((1, 2, 3)))
    b4 = msgpack_dumps(Named(x=1, y=2, z=3))
    assert b2 == b1
    assert b3 == b1
    assert b4 == b1
    assert msgpack_loads(b1) == [1, 2, 3]
    assert msgpack_loads(b1, use_list=False) == (1, 2, 3)


def test_msgpack_custom_encoder_decoder():
    class CustomObject:
        def __init__(self, value):
            self.value = value

    def serialize_obj(obj):
        if isinstance(obj, CustomObject):
            return {"__custom__": obj.value}
        return obj

    def deserialize_obj(obj):
        if "__custom__" in obj:
            return CustomObject(obj["__custom__"])
        return obj

    data = {"a": 123, "b": CustomObject({"foo": "bar"})}
    with pytest.raises(TypeError):
        msgpack_dumps(data)

    # Register custom encoders/decoders to handle CustomObject
    msgpack_encoders.register("custom_object", func=serialize_obj)
    msgpack_decoders.register("custom_object", func=deserialize_obj)
    bytes_data = msgpack_dumps(data)
    new_data = msgpack_loads(bytes_data)
    assert new_data["a"] == 123
    assert isinstance(new_data["b"], CustomObject)
    assert new_data["b"].value == {"foo": "bar"}

    # Test that it also works with combinations of encoders/decoders (e.g. complex)
    data = {"a": 1 + 2j, "b": CustomObject({"foo": "bar"})}
    bytes_data = msgpack_dumps(data)
    new_data = msgpack_loads(bytes_data)
    assert isinstance(new_data["a"], complex)
    assert isinstance(new_data["b"], CustomObject)
    assert new_data["b"].value == {"foo": "bar"}

    # Clean up
    msgpack_encoders.deregister("custom_object")
    msgpack_decoders.deregister("custom_object")


def test_msgpack_custom_subtype_handler():
    """By default, subtypes of base types are cast to their parents.
    Test that the user can define a custom encoder/decoder to preserve
    the subtype.
    """

    class MyInt(int):
        pass

    def encode_myint(obj):
        if isinstance(obj, MyInt):
            return {"MyInt": int(obj)}
        return obj

    def decode_myint(obj):
        if "MyInt" in obj:
            return MyInt(obj["MyInt"])
        return obj

    inp = MyInt(5)
    out = msgpack_loads(msgpack_dumps(inp))
    assert out == 5
    assert type(out) is int

    msgpack_encoders.register("myint", func=encode_myint)
    msgpack_decoders.register("myint", func=decode_myint)
    out = msgpack_loads(msgpack_dumps(inp))
    assert out == MyInt(5)
    assert type(out) is MyInt

    # Cleanup
    msgpack_encoders.deregister("myint")
    msgpack_decoders.deregister("myint")


def test_msgpack_numpy_not_installed():
    """Test that we get a clean ModuleNotFoundError when
    trying to decode numpy data when numpy is not installed.
    """
    # Output of np.float64(1)
    bin = (
        b"\x83\xc4\x02nd\xc2\xc4\x04type\xa3<f8\xc4\x04"
        b"data\xc4\x08\x00\x00\x00\x00\x00\x00\xf0?"
    )
    try:
        import numpy as np

        out = msgpack_loads(bin)
        assert out == np.float64(1)
        assert type(out) is np.float64
    except ModuleNotFoundError:
        with pytest.raises(ModuleNotFoundError, match="numpy"):
            msgpack_loads(bin)
