# coding: utf8
from __future__ import unicode_literals

from .._pickle_api import pickle_dumps, pickle_loads


def test_pickle_dumps():
    data = {"hello": "world", "test": 123}
    expected = b"\x80\x04\x95\x1e\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x05hello\x94\x8c\x05world\x94\x8c\x04test\x94K{u."
    msg = pickle_dumps(data)
    assert msg == expected


def test_pickle_loads():
    msg = b"\x80\x04\x95\x1e\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x05hello\x94\x8c\x05world\x94\x8c\x04test\x94K{u."
    data = pickle_loads(msg)
    assert len(data) == 2
    assert data["hello"] == "world"
    assert data["test"] == 123
