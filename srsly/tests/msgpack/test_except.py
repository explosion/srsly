from pytest import raises
import datetime
from srsly.msgpack import packb, unpackb, Unpacker, FormatError, StackError, OutOfData


class DummyException(Exception):
    pass


def test_raise_on_find_unsupported_value():
    with raises(TypeError):
        packb(datetime.datetime.now())


def test_raise_from_object_hook():
    def hook(obj):
        raise DummyException

    raises(DummyException, unpackb, packb({}), object_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": "buzz"}), object_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": "buzz"}), object_pairs_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": {"buzz": "spam"}}), object_hook=hook)
    raises(
        DummyException,
        unpackb,
        packb({"fizz": {"buzz": "spam"}}),
        object_pairs_hook=hook,
    )


def test_unpacker_raise_from_object_hook():
    def hook(obj):
        raise DummyException

    up = Unpacker(object_hook=hook)

    def up_unpack(x):
        up.feed(x)
        return up.unpack()

    raises(DummyException, up_unpack, packb({}))
    raises(DummyException, up_unpack, packb({"fizz": "buzz"}))
    raises(DummyException, up_unpack, packb({"fizz": "buzz"}))
    raises(DummyException, up_unpack, packb({"fizz": {"buzz": "spam"}}))
    raises(DummyException, up_unpack, packb({"fizz": {"buzz": "spam"}}))


def test_invalidvalue():
    incomplete = b"\xd9\x97#DL_"  # raw8 - length=0x97
    with raises(ValueError):
        unpackb(incomplete)

    with raises(OutOfData):
        unpacker = Unpacker()
        unpacker.feed(incomplete)
        unpacker.unpack()

    with raises(FormatError):
        unpackb(b"\xc1")  # (undefined tag)

    with raises(FormatError):
        unpackb(b"\x91\xc1")  # fixarray(len=1) [ (undefined tag) ]

    with raises(StackError):
        unpackb(b"\x91" * 3000)  # nested fixarray(len=1)


def test_strict_map_key():
    valid = {u"unicode": 1, b"bytes": 2}
    packed = packb(valid, use_bin_type=True)
    assert valid == unpackb(packed, raw=False, strict_map_key=True)

    invalid = {42: 1}
    packed = packb(invalid, use_bin_type=True)
    with raises(ValueError):
        unpackb(packed, raw=False, strict_map_key=True)


def test_unpacker_should_not_crash_after_exception():
    # CVE-2026-57585: reusing an Unpacker after a failed unpack resumed from a
    # corrupt parser context and could segfault.
    up = Unpacker(strict_map_key=True)
    up.feed(b"\x83\x73\xc4\x00")  # fixmap(3): int key (rejected) + empty bin8
    with raises(ValueError):
        up.unpack()  # int is not allowed for map key
    up.skip()  # SIGSEGV before the fix


def test_unpacker_usable_after_exception():
    up = Unpacker(strict_map_key=True, raw=False)
    up.feed(packb({42: 1}))
    with raises(ValueError):
        up.unpack()
    # The parser stops on the rejected value, then resumes from a clean state.
    up.feed(packb({"a": [1, 2, {"b": 3}]}))
    assert list(up) == [1, {"a": [1, 2, {"b": 3}]}]
