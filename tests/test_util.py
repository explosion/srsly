# coding: utf8
from __future__ import unicode_literals

import pytest
import os
import tempfile
from pathlib import Path
from contextlib import contextmanager

from srsly.util import read_json, write_json, read_jsonl, write_jsonl
from srsly.util import is_json_serializable


@contextmanager
def make_tempfile(data=None):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    if data is not None:
        with Path(tmp_file.name).open("w", encoding="utf8") as f:
            f.write(data)
    yield tmp_file.name
    os.remove(tmp_file.name)


def test_read_json_file():
    file_contents = '{\n    "hello": "world"\n}'
    with make_tempfile(file_contents) as file_path:
        data = read_json(file_path)
    assert len(data) == 1
    assert data["hello"] == "world"


def test_read_json_file_invalid():
    file_contents = '{\n    "hello": world\n}'
    with make_tempfile(file_contents) as file_path:
        with pytest.raises(ValueError):
            data = read_json(file_path)


def test_write_json_file():
    data = {"hello": "word", "test": 123}
    with make_tempfile() as file_path:
        write_json(file_path, data)
        with Path(file_path).open("r", encoding="utf8") as f:
            assert f.read() == '{\n  "hello":"word",\n  "test":123\n}'


def test_read_jsonl_file():
    file_contents = '{"hello": "world"}\n{"test": 123}'
    with make_tempfile(file_contents) as f:
        data = read_jsonl(f)
        # Make sure this returns a generator, not just a list
        assert not hasattr(data, "__len__")
        data = list(data)
    assert len(data) == 2
    assert len(data[0]) == 1
    assert len(data[1]) == 1
    assert data[0]["hello"] == "world"
    assert data[1]["test"] == 123


def test_read_jsonl_file_invalid():
    file_contents = '{"hello": world}\n{"test": 123}'
    with make_tempfile(file_contents) as f:
        with pytest.raises(ValueError):
            data = list(read_jsonl(f))
        data = list(read_jsonl(f, skip=True))
    assert len(data) == 1
    assert len(data[0]) == 1
    assert data[0]["test"] == 123


def test_write_json_file():
    data = [{"hello": "world"}, {"test": 123}]
    with make_tempfile() as file_path:
        write_jsonl(file_path, data)
        with Path(file_path).open("r", encoding="utf8") as f:
            assert f.read() == '{"hello":"world"}\n{"test":123}\n'


@pytest.mark.parametrize(
    "obj,expected",
    [
        (["a", "b", 1, 2], True),
        ({"a": "b", "c": 123}, True),
        ("hello", True),
        (lambda x: x, False),
    ],
)
def test_is_json_serializable(obj, expected):
    assert is_json_serializable(obj) == expected
