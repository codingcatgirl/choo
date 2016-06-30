import os

__version__ = '0.2.0'

if os.environ.get('CHOO_NOIMPORT') != '1':
    from . import apis  # prevent circular imports  # noqa
    from .types import Serializable
    Serializable._collect_serializables()
