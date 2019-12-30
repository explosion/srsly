from typing import Optional

from . import cloudpickle
from .types import JSONObject


def pickle_dumps(data: JSONObject, protocol: Optional[int] = None) -> bytes:
    """Serialize a Python object with pickle.

    data: The object to serialize.
    protocol (int): Protocol to use. -1 for highest.
    RETURNS (bytes): The serialized object.
    """
    return cloudpickle.dumps(data, protocol=protocol)


def pickle_loads(data: bytes) -> JSONObject:
    """Deserialize bytes with pickle.

    data (bytes): The data to deserialize.
    RETURNS: The deserialized Python object.
    """
    return cloudpickle.loads(data)
