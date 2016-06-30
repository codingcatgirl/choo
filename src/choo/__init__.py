try:
    from . import apis  # prevent circular imports  # noqa
except ImportError:
    # catch exception so __version__ can be imported without all dependencies installed
    pass
else:
    from .types import Serializable
    Serializable._collect_serializables()

__version__ = '0.2.0'
