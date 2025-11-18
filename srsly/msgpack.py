from msgpack import *

# Old msgpack API, removed upstream and reimplemented in srsly
# for backwards compatiblity.
from ._msgpack_api import msgpack_encoders, msgpack_decoders
