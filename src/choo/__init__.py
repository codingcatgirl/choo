try:
    from . import apis  # prevent circular imports  # noqa
except ImportError:
    pass  # users will get the exception anyway when they try to import apis

__version__ = '0.2.0'
