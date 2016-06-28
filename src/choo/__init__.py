try:
    from . import networks  # prevent circular imports  # noqa
except ImportError:
    pass  # users will get the exception anyway when they try to import networks

__version__ = '0.2.0'
