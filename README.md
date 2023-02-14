<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# srsly: Modern high-performance serialization utilities for Python

This package bundles some of the best Python serialization libraries into one
standalone package, with a high-level API that makes it easy to write code
that's correct across platforms and Pythons. This allows us to provide all the
serialization utilities we need in a single binary wheel. Currently supports **JSON**, **JSONL**, **MessagePack**, **Pickle** and **YAML**.

[![Azure Pipelines](https://img.shields.io/azure-devops/build/explosion-ai/public/4/master.svg?logo=azure-pipelines&style=flat-square)](https://dev.azure.com/explosion-ai/public/_build?definitionId=4)
[![PyPi](https://img.shields.io/pypi/v/srsly.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.python.org/pypi/srsly)
[![conda](https://img.shields.io/conda/vn/conda-forge/srsly.svg?style=flat-square&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/srsly)
[![GitHub](https://img.shields.io/github/release/explosion/srsly/all.svg?style=flat-square&logo=github)](https://github.com/explosion/srsly)
[![Python wheels](https://img.shields.io/badge/wheels-%E2%9C%93-4c1.svg?longCache=true&style=flat-square&logo=python&logoColor=white)](https://github.com/explosion/wheelwright/releases)

## Motivation

Serialization is hard, especially across Python versions and multiple platforms.
After dealing with many subtle bugs over the years (encodings, locales, large
files) our libraries like [spaCy](https://github.com/explosion/spaCy) and
[Prodigy](https://prodi.gy) had steadily grown a number of utility functions to
wrap the multiple serialization formats we need to support (especially `json`,
`msgpack` and `pickle`). These wrapping functions ended up duplicated across our
codebases, so we wanted to put them in one place.

At the same time, we noticed that having a lot of small dependencies was making
maintenance harder, and making installation slower. To solve this, we've made
`srsly` standalone, by including the component packages directly within it. This
way we can provide all the serialization utilities we need in a single binary
wheel.

`srsly` currently includes forks of the following packages:

- [`ujson`](https://github.com/esnme/ultrajson)
- [`msgpack`](https://github.com/msgpack/msgpack-python)
- [`msgpack-numpy`](https://github.com/lebedov/msgpack-numpy)
- [`cloudpickle`](https://github.com/cloudpipe/cloudpickle)
- [`ruamel.yaml`](https://github.com/pycontribs/ruamel-yaml) (without unsafe implementations!)

## Installation

> ⚠️ Note that `v2.x` is only compatible with **Python 3.6+**. For 2.7+ compatibility, use `v1.x`.

`srsly` can be installed from pip. Before installing, make sure that your `pip`,
`setuptools` and `wheel` are up to date.

```bash
python -m pip install -U pip setuptools wheel
python -m pip install srsly
```

Or from conda via conda-forge:

```bash
conda install -c conda-forge srsly
```

Alternatively, you can also compile the library from source. You'll need to make
sure that you have a development environment with a Python distribution
including header files, a compiler (XCode command-line tools on macOS / OS X or
Visual C++ build tools on Windows), pip and git installed.

Install from source:

```bash
# clone the repo
git clone https://github.com/explosion/srsly
cd srsly

# create a virtual environment
python -m venv .env
source .env/bin/activate

# update pip
python -m pip install -U pip setuptools wheel

# compile and install from source
python -m pip install .
```

For developers, install requirements separately and then install in editable
mode without build isolation:

```bash
# install in editable mode
python -m pip install -r requirements.txt
python -m pip install --no-build-isolation --editable .

# run test suite
python -m pytest --pyargs srsly
```

## API

### JSON

> 📦 The underlying module is exposed via `srsly.ujson`. However, we normally
> interact with it via the utility functions only.

#### <kbd>function</kbd> `srsly.json_dumps`

Serialize an object to a JSON string. Falls back to `json` if `sort_keys=True` is used (until it's fixed in `ujson`).

```python
data = {"foo": "bar", "baz": 123}
json_string = srsly.json_dumps(data)
```

| Argument    | Type | Description                                            |
| ----------- | ---- | ------------------------------------------------------ |
| `data`      | -    | The JSON-serializable data to output.                  |
| `indent`    | int  | Number of spaces used to indent JSON. Defaults to `0`. |
| `sort_keys` | bool | Sort dictionary keys. Defaults to `False`.             |
| **RETURNS** | str  | The serialized string.                                 |

#### <kbd>function</kbd> `srsly.json_loads`

Deserialize unicode or bytes to a Python object.

```python
data = '{"foo": "bar", "baz": 123}'
obj = srsly.json_loads(data)
```

| Argument    | Type        | Description                     |
| ----------- | ----------- | ------------------------------- |
| `data`      | str / bytes | The data to deserialize.        |
| **RETURNS** | -           | The deserialized Python object. |

#### <kbd>function</kbd> `srsly.write_json`

Create a JSON file and dump contents or write to standard output.

```python
data = {"foo": "bar", "baz": 123}
srsly.write_json("/path/to/file.json", data)
```

| Argument | Type         | Description                                            |
| -------- | ------------ | ------------------------------------------------------ |
| `path`   | str / `Path` | The file path or `"-"` to write to stdout.             |
| `data`   | -            | The JSON-serializable data to output.                  |
| `indent` | int          | Number of spaces used to indent JSON. Defaults to `2`. |

#### <kbd>function</kbd> `srsly.read_json`

Load JSON from a file or standard input.

```python
data = srsly.read_json("/path/to/file.json")
```

| Argument    | Type         | Description                                |
| ----------- | ------------ | ------------------------------------------ |
| `path`      | str / `Path` | The file path or `"-"` to read from stdin. |
| **RETURNS** | dict / list  | The loaded JSON content.                   |

#### <kbd>function</kbd> `srsly.write_gzip_json`

Create a gzipped JSON file and dump contents.

```python
data = {"foo": "bar", "baz": 123}
srsly.write_gzip_json("/path/to/file.json.gz", data)
```

| Argument | Type         | Description                                            |
| -------- | ------------ | ------------------------------------------------------ |
| `path`   | str / `Path` | The file path.                                         |
| `data`   | -            | The JSON-serializable data to output.                  |
| `indent` | int          | Number of spaces used to indent JSON. Defaults to `2`. |

#### <kbd>function</kbd> `srsly.write_gzip_jsonl`

Create a gzipped JSONL file and dump contents.

```python
data = [{"foo": "bar"}, {"baz": 123}]
srsly.write_gzip_json("/path/to/file.jsonl.gz", data)
```

| Argument          | Type         | Description                                                                                                                                                                                                             |
| ----------------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`            | str / `Path` | The file path.                                                                                                                                                                                                          |
| `lines`           | -            | The JSON-serializable contents of each line.                                                                                                                                                                            |
| `append`          | bool         | Whether or not to append to the location. Appending to .gz files is generally not recommended, as it doesn't allow the algorithm to take advantage of all data when compressing - files may hence be poorly compressed. |
| `append_new_line` | bool         | Whether or not to write a new line before appending to the file.                                                                                                                                                        |

#### <kbd>function</kbd> `srsly.read_gzip_json`

Load gzipped JSON from a file.

```python
data = srsly.read_gzip_json("/path/to/file.json.gz")
```

| Argument    | Type         | Description              |
| ----------- | ------------ | ------------------------ |
| `path`      | str / `Path` | The file path.           |
| **RETURNS** | dict / list  | The loaded JSON content. |

#### <kbd>function</kbd> `srsly.read_gzip_jsonl`

Load gzipped JSONL from a file.

```python
data = srsly.read_gzip_jsonl("/path/to/file.jsonl.gz")
```

| Argument    | Type         | Description               |
| ----------- | ------------ | ------------------------- |
| `path`      | str / `Path` | The file path.            |
| **RETURNS** | dict / list  | The loaded JSONL content. |

#### <kbd>function</kbd> `srsly.write_jsonl`

Create a JSONL file (newline-delimited JSON) and dump contents line by line, or
write to standard output.

```python
data = [{"foo": "bar"}, {"baz": 123}]
srsly.write_jsonl("/path/to/file.jsonl", data)
```

| Argument          | Type         | Description                                                                                                            |
| ----------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `path`            | str / `Path` | The file path or `"-"` to write to stdout.                                                                             |
| `lines`           | iterable     | The JSON-serializable lines.                                                                                           |
| `append`          | bool         | Append to an existing file. Will open it in `"a"` mode and insert a newline before writing lines. Defaults to `False`. |
| `append_new_line` | bool         | Defines whether a new line should first be written when appending to an existing file. Defaults to `True`.             |

#### <kbd>function</kbd> `srsly.read_jsonl`

Read a JSONL file (newline-delimited JSON) or from JSONL data from standard
input and yield contents line by line. Blank lines will always be skipped.

```python
data = srsly.read_jsonl("/path/to/file.jsonl")
```

| Argument   | Type       | Description                                                          |
| ---------- | ---------- | -------------------------------------------------------------------- |
| `path`     | str / Path | The file path or `"-"` to read from stdin.                           |
| `skip`     | bool       | Skip broken lines and don't raise `ValueError`. Defaults to `False`. |
| **YIELDS** | -          | The loaded JSON contents of each line.                               |

#### <kbd>function</kbd> `srsly.is_json_serializable`

Check if a Python object is JSON-serializable.

```python
assert srsly.is_json_serializable({"hello": "world"}) is True
assert srsly.is_json_serializable(lambda x: x) is False
```

| Argument    | Type | Description                              |
| ----------- | ---- | ---------------------------------------- |
| `obj`       | -    | The object to check.                     |
| **RETURNS** | bool | Whether the object is JSON-serializable. |

### msgpack

> 📦 The underlying module is exposed via `srsly.msgpack`. However, we normally
> interact with it via the utility functions only.

#### <kbd>function</kbd> `srsly.msgpack_dumps`

Serialize an object to a msgpack byte string.

```python
data = {"foo": "bar", "baz": 123}
msg = srsly.msgpack_dumps(data)
```

| Argument    | Type  | Description            |
| ----------- | ----- | ---------------------- |
| `data`      | -     | The data to serialize. |
| **RETURNS** | bytes | The serialized bytes.  |

#### <kbd>function</kbd> `srsly.msgpack_loads`

Deserialize msgpack bytes to a Python object.

```python
msg = b"\x82\xa3foo\xa3bar\xa3baz{"
data = srsly.msgpack_loads(msg)
```

| Argument    | Type  | Description                                                                             |
| ----------- | ----- | --------------------------------------------------------------------------------------- |
| `data`      | bytes | The data to deserialize.                                                                |
| `use_list`  | bool  | Don't use tuples instead of lists. Can make deserialization slower. Defaults to `True`. |
| **RETURNS** | -     | The deserialized Python object.                                                         |

#### <kbd>function</kbd> `srsly.write_msgpack`

Create a msgpack file and dump contents.

```python
data = {"foo": "bar", "baz": 123}
srsly.write_msgpack("/path/to/file.msg", data)
```

| Argument | Type         | Description            |
| -------- | ------------ | ---------------------- |
| `path`   | str / `Path` | The file path.         |
| `data`   | -            | The data to serialize. |

#### <kbd>function</kbd> `srsly.read_msgpack`

Load a msgpack file.

```python
data = srsly.read_msgpack("/path/to/file.msg")
```

| Argument    | Type         | Description                                                                             |
| ----------- | ------------ | --------------------------------------------------------------------------------------- |
| `path`      | str / `Path` | The file path.                                                                          |
| `use_list`  | bool         | Don't use tuples instead of lists. Can make deserialization slower. Defaults to `True`. |
| **RETURNS** | -            | The loaded and deserialized content.                                                    |

### pickle

> 📦 The underlying module is exposed via `srsly.cloudpickle`. However, we
> normally interact with it via the utility functions only.

#### <kbd>function</kbd> `srsly.pickle_dumps`

Serialize a Python object with pickle.

```python
data = {"foo": "bar", "baz": 123}
pickled_data = srsly.pickle_dumps(data)
```

| Argument    | Type  | Description                                            |
| ----------- | ----- | ------------------------------------------------------ |
| `data`      | -     | The object to serialize.                               |
| `protocol`  | int   | Protocol to use. `-1` for highest. Defaults to `None`. |
| **RETURNS** | bytes | The serialized object.                                 |

#### <kbd>function</kbd> `srsly.pickle_loads`

Deserialize bytes with pickle.

```python
pickled_data = b"\x80\x04\x95\x19\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x03foo\x94\x8c\x03bar\x94\x8c\x03baz\x94K{u."
data = srsly.pickle_loads(pickled_data)
```

| Argument    | Type  | Description                     |
| ----------- | ----- | ------------------------------- |
| `data`      | bytes | The data to deserialize.        |
| **RETURNS** | -     | The deserialized Python object. |

### YAML

> 📦 The underlying module is exposed via `srsly.ruamel_yaml`. However, we normally
> interact with it via the utility functions only.

#### <kbd>function</kbd> `srsly.yaml_dumps`

Serialize an object to a YAML string. See the [`ruamel.yaml` docs](https://yaml.readthedocs.io/en/latest/detail.html?highlight=indentation#indentation-of-block-sequences) for details on the indentation format.

```python
data = {"foo": "bar", "baz": 123}
yaml_string = srsly.yaml_dumps(data)
```

| Argument          | Type | Description                                |
| ----------------- | ---- | ------------------------------------------ |
| `data`            | -    | The JSON-serializable data to output.      |
| `indent_mapping`  | int  | Mapping indentation. Defaults to `2`.      |
| `indent_sequence` | int  | Sequence indentation. Defaults to `4`.     |
| `indent_offset`   | int  | Indentation offset. Defaults to `2`.       |
| `sort_keys`       | bool | Sort dictionary keys. Defaults to `False`. |
| **RETURNS**       | str  | The serialized string.                     |

#### <kbd>function</kbd> `srsly.yaml_loads`

Deserialize unicode or a file object to a Python object.

```python
data = 'foo: bar\nbaz: 123'
obj = srsly.yaml_loads(data)
```

| Argument    | Type       | Description                     |
| ----------- | ---------- | ------------------------------- |
| `data`      | str / file | The data to deserialize.        |
| **RETURNS** | -          | The deserialized Python object. |

#### <kbd>function</kbd> `srsly.write_yaml`

Create a YAML file and dump contents or write to standard output.

```python
data = {"foo": "bar", "baz": 123}
srsly.write_yaml("/path/to/file.yml", data)
```

| Argument          | Type         | Description                                |
| ----------------- | ------------ | ------------------------------------------ |
| `path`            | str / `Path` | The file path or `"-"` to write to stdout. |
| `data`            | -            | The JSON-serializable data to output.      |
| `indent_mapping`  | int          | Mapping indentation. Defaults to `2`.      |
| `indent_sequence` | int          | Sequence indentation. Defaults to `4`.     |
| `indent_offset`   | int          | Indentation offset. Defaults to `2`.       |
| `sort_keys`       | bool         | Sort dictionary keys. Defaults to `False`. |

#### <kbd>function</kbd> `srsly.read_yaml`

Load YAML from a file or standard input.

```python
data = srsly.read_yaml("/path/to/file.yml")
```

| Argument    | Type         | Description                                |
| ----------- | ------------ | ------------------------------------------ |
| `path`      | str / `Path` | The file path or `"-"` to read from stdin. |
| **RETURNS** | dict / list  | The loaded YAML content.                   |

#### <kbd>function</kbd> `srsly.is_yaml_serializable`

Check if a Python object is YAML-serializable.

```python
assert srsly.is_yaml_serializable({"hello": "world"}) is True
assert srsly.is_yaml_serializable(lambda x: x) is False
```

| Argument    | Type | Description                              |
| ----------- | ---- | ---------------------------------------- |
| `obj`       | -    | The object to check.                     |
| **RETURNS** | bool | Whether the object is YAML-serializable. |
