from unittest import TestCase
import pytest

pytest.importorskip("numpy", reason="numpy is required for these tests")

from srsly import msgpack_dumps, msgpack_loads
import numpy as np
from numpy.testing import assert_equal, assert_array_equal


class test_numpy_msgpack(TestCase):
    def encode_decode(self, x):
        x_enc = msgpack_dumps(x)
        return msgpack_loads(x_enc)

    def test_numpy_scalar_bool(self):
        x = np.bool_(True)
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))
        x = np.bool_(False)
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_numpy_scalar_float(self):
        x = np.float32(np.random.rand())
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_numpy_scalar_complex(self):
        x = np.complex64(np.random.rand() + 1j * np.random.rand())
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_scalar_float(self):
        x = np.random.rand()
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_scalar_complex(self):
        x = np.random.rand() + 1j * np.random.rand()
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_list_numpy_float(self):
        x = [np.float32(np.random.rand()) for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x], [type(e) for e in x_rec])

    def test_list_numpy_float_complex(self):
        x = [np.float32(np.random.rand()) for i in range(5)] + [
            np.complex128(np.random.rand() + 1j * np.random.rand()) for i in range(5)
        ]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x], [type(e) for e in x_rec])

    def test_list_float(self):
        x = [np.random.rand() for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x], [type(e) for e in x_rec])

    def test_list_float_complex(self):
        x = [(np.random.rand() + 1j * np.random.rand()) for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x], [type(e) for e in x_rec])

    def test_list_str(self):
        x = [b"x" * i for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x_rec], [bytes] * 5)

    def test_dict_float(self):
        x = {b"foo": 1.0, b"bar": 2.0}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values()), sorted(x_rec.values()))
        assert_array_equal(
            [type(e) for e in sorted(x.values())],
            [type(e) for e in sorted(x_rec.values())],
        )
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal(
            [type(e) for e in sorted(x.keys())], [type(e) for e in sorted(x_rec.keys())]
        )

    def test_dict_complex(self):
        x = {b"foo": 1.0 + 1.0j, b"bar": 2.0 + 2.0j}
        x_rec = self.encode_decode(x)
        assert_array_equal(
            sorted(x.values(), key=np.linalg.norm),
            sorted(x_rec.values(), key=np.linalg.norm),
        )
        assert_array_equal(
            [type(e) for e in sorted(x.values(), key=np.linalg.norm)],
            [type(e) for e in sorted(x_rec.values(), key=np.linalg.norm)],
        )
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal(
            [type(e) for e in sorted(x.keys())], [type(e) for e in sorted(x_rec.keys())]
        )

    def test_dict_str(self):
        x = {b"foo": b"xxx", b"bar": b"yyyy"}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values()), sorted(x_rec.values()))
        assert_array_equal(
            [type(e) for e in sorted(x.values())],
            [type(e) for e in sorted(x_rec.values())],
        )
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal(
            [type(e) for e in sorted(x.keys())], [type(e) for e in sorted(x_rec.keys())]
        )

    def test_dict_numpy_float(self):
        x = {b"foo": np.float32(1.0), b"bar": np.float32(2.0)}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values()), sorted(x_rec.values()))
        assert_array_equal(
            [type(e) for e in sorted(x.values())],
            [type(e) for e in sorted(x_rec.values())],
        )
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal(
            [type(e) for e in sorted(x.keys())], [type(e) for e in sorted(x_rec.keys())]
        )

    def test_dict_numpy_complex(self):
        x = {b"foo": np.complex128(1.0 + 1.0j), b"bar": np.complex128(2.0 + 2.0j)}
        x_rec = self.encode_decode(x)
        assert_array_equal(
            sorted(x.values(), key=np.linalg.norm),
            sorted(x_rec.values(), key=np.linalg.norm),
        )
        assert_array_equal(
            [type(e) for e in sorted(x.values(), key=np.linalg.norm)],
            [type(e) for e in sorted(x_rec.values(), key=np.linalg.norm)],
        )
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal(
            [type(e) for e in sorted(x.keys())], [type(e) for e in sorted(x_rec.keys())]
        )

    def test_numpy_array_float(self):
        x = np.random.rand(5).astype(np.float32)
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_complex(self):
        x = (np.random.rand(5) + 1j * np.random.rand(5)).astype(np.complex128)
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_float_2d(self):
        x = np.random.rand(5, 5).astype(np.float32)
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_str(self):
        x = np.array([b"aaa", b"bbbb", b"ccccc"])
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_mixed(self):
        x = np.array(
            [(1, 2, b"a", [1.0, 2.0])],
            np.dtype(
                [
                    ("arg0", np.uint32),
                    ("arg1", np.uint32),
                    ("arg2", "S1"),
                    ("arg3", np.float32, (2,)),
                ]
            ),
        )
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_noncontiguous(self):
        x = np.ones((10, 10), np.uint32)[0:5, 0:5]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_list_mixed(self):
        x = [1.0, np.float32(3.5), np.complex128(4.25), b"foo"]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x], [type(e) for e in x_rec])
