from typing import Union, Dict, Any, List, Tuple
from enum import Enum
from collections import OrderedDict
from pathlib import Path


# String marker for standard input / output (can only be "-")
class StandardIO(str, Enum):
    dash: str = "-"


FilePath = Union[str, Path]

# https://github.com/python/typing/issues/182#issuecomment-186684288
JSONOutput = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
# For input, we also accept tuples, ordered dicts etc.
JSONInput = Union[
    str, int, float, bool, None, Dict[str, Any], List[Any], Tuple[Any], OrderedDict
]
