from typing import Union, Dict, Any, List
from enum import Enum
from pathlib import Path


# String marker for standard input / output (can only be "-")
class StandardIO(str, Enum):
    dash: str = "-"


FilePath = Union[str, Path]

# https://github.com/python/typing/issues/182#issuecomment-186684288
JSONObject = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
