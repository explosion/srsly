# coding: utf8
from __future__ import unicode_literals

from . import cloudpickle


def pickle_dumps(data, protocol=None):
    return cloudpickle.dumps(data, protocol=protocol)


def pickle_loads(data):
    return cloudpickle.loads(data)
