import pytest

np = pytest.importorskip("numpy", reason="numpy is required for these tests")

from srsly import msgpack_dumps, msgpack_loads, read_msgpack, write_msgpack


@pytest.mark.parametrize(
    "fields",
    [
        [("id", "i4"), ("point", [("x", "i4"), ("y", "f8")])],
        [
            ("id", "i4"),
            ("record", [("point", [("x", "i4"), ("y", "f8")]), ("label", "U4")]),
        ],
        [("id", "i4"), ("points", [("x", "i4"), ("y", "f8")], (2,))],
    ],
    ids=["nested", "deeply-nested", "nested-subarray"],
)
@pytest.mark.parametrize("use_list", [True, False])
@pytest.mark.parametrize("storage", ["memory", "file"])
def test_nested_structured_array_roundtrip(fields, use_list, storage, tmp_path):
    data = np.zeros((2, 3), dtype=fields)
    data["id"] = np.arange(6).reshape(2, 3)
    records = data[data.dtype.names[1]]
    if "point" in records.dtype.names:
        records["label"] = "café"
        records = records["point"]
    records["x"] = 42
    records["y"] = 1.25

    if storage == "memory":
        result = msgpack_loads(msgpack_dumps(data), use_list=use_list)
    else:
        path = tmp_path / "records.msgpack"
        write_msgpack(path, data)
        result = read_msgpack(path, use_list=use_list)

    assert result.dtype == data.dtype
    assert result.shape == data.shape
    np.testing.assert_array_equal(result, data)
