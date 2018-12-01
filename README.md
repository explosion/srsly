<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# srsly: Modern high-performance serialization utilities for Python

This package bundles some of the best Python serialization libraries into one standalone package, with a high-level API that makes it easy to write code
that's correct across platforms and Pythons. This allows us to provide all the
serialization utilities we need in a single binary wheel.

⚠️ **Still under construction!**

[![Travis](https://img.shields.io/travis/explosion/srsly/master.svg?style=flat-square&logo=travis)](https://travis-ci.org/explosion/srsly)
[![Appveyor](https://img.shields.io/appveyor/ci/explosion/srsly/master.svg?style=flat-square&logo=appveyor)](https://ci.appveyor.com/project/explosion/srsly)
[![PyPi](https://img.shields.io/pypi/v/srsly.svg?style=flat-square)](https://pypi.python.org/pypi/srlsy)
[![GitHub](https://img.shields.io/github/release/explosion/srsly/all.svg?style=flat-square)](https://github.com/explosion/srsly)

## Motivation

Serialization is hard, especially across Python versions and multiple platforms.
After dealing with many subtle bugs over the years (encodings, locales, large
files) our libraries like [spaCy](https://github.com/explosion/spaCy) and
[Prodigy](https://prodi.gy) have steadily grown a number of utility functions to
wrap the multiple serialization formats we need to support (especially `json`,
`msgpack` and `pickle`). These wrapping functions ended up duplicated across our
codebases, so we wanted to put them in one place.

At the same time, we noticed that having a lot of small dependencies was making
maintainence harder, and making installation slower. To solve this, we've made
`srsly` standalone, by including the component packages directly within it. This
way we can provide all the serialization utilities we need in a single binary
wheel.

`srsly` currently includes forks of the following packages:

* [`ujson`](https://github.com/esnme/ultrajson)
* [`msgpack`](https://github.com/msgpack/msgpack-python)
* [`msgpack-numpy`](https://github.com/lebedov/msgpack-numpy)
* [`cloudpickle`](https://github.com/cloudpipe/cloudpickle)

## Installation

`srsly` can be installed from pip:

```bash
pip install srsly
```

Alternatively, you can also comile the library from source. You'll need to make
sure that you have a development environment consisting of a Python distribution
including header files, a compiler (XCode command-line tools on macOS / OS X or
Visual C++ build tools on Windows), pip, virtualenv and git installed.

```bash
pip install -r requirements.txt  # install development dependencies
python setup.py build_ext --inplace  # compile the library
```

## API

### <kbd>function</kbd> `srsly.read_json`

Load JSON from a file or standard input.

```python
data = srsly.read_json("/path/to/file.json")
```

| Argument | Type | Description |
| --- | --- | --- |
| `location` | unicode / `Path` | The file path or `"-"` to read from stdin. |
| **RETURNS** | dict / list | The loaded JSON content. |

### <kbd>function</kbd> `srsly.write_json`

Create a JSON file and dump contents or write to standard output.

```python
data = {"foo": "bar", "baz": 123}
srsly.write_json("/path/to/file.jsonl", data)
```

| Argument | Type | Description |
| --- | --- | --- |
| `location` | unicode / `Path` | The file path or `"-"` to write to stdout. |
| `data` | - | The JSON-serializable data to output. |
| `indent` | int | Number of spaces used to indent JSON. Default to `2`. |

### <kbd>function</kbd> `srsly.read_jsonl`

Read a JSONL file (newline-delimited JSON) or from JSONL data from
standard input and yield contents line by line. Blank lines will always be
skipped.

```python
data = srsly.read_jsonl("/path/to/file.jsonl")
```

| Argument | Type | Description |
| --- | --- | --- |
| `location` | unicode / Path | The file path or `"-"` to read from stdin. |
| `skip` | bool | Skip broken lines and don't raise `ValueError`. Defaults to `False`. |
| **YIELDS** | - | The loaded JSON contents of each line. |

### <kbd>function</kbd> `srsly.write_jsonl`

Create a JSONL file (newline-delimited JSON) and dump contents line by line, or
write to standard output.

```python
data = [{"foo": "bar"}, {"baz": 123}]
srsly.write_jsonl("/path/to/file.jsonl", data)
```

| Argument | Type | Description |
| --- | --- | --- |
| `location` | unicode / `Path` | The file path or `"-"` to write to stdout. |
| `lines` | iterable | The JSON-serializable lines. |

### <kbd>function</kbd> `srsly.is_json_serializable`

Check if a Python object is JSON-serializable.

```python
assert srsly.is_json_serializable({"hello": "world"}) is True
assert srsly.is_json_serializable(lambda x: x) is False
```

| Argument | Type | Description |
| --- | --- | --- |
| `obj` | - | The object to check. |
| **RETURNS** | bool | Whether the object is JSON-serializable. |
