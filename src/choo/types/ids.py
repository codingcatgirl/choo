from collections import namedtuple

from .misc import Serializable


class IDs(Serializable):
    """
    A Mapping of ids by id namespace (e.g. 'vrr' for the id namespace of the VRR network)
    Multiple ids per namespace are possible.
    IDs instances can be combined like sets.

    How to initializ:
    >>> ids = IDs((('one_id', '1a'), ('multiple_ids', 2), ('multiple_ids', 3)))
    >>> ids = IDs({'one_id': '1a', 'multiple_ids': (2, 3)})

    How to retrieve data:
    >>> ids['multiple_ids']  # returns 2 or 3
    >>> ids.getall('multiple_ids')  # returns set((2, 3))
    >>> ids['other_namespace']  # KeyError
    >>> ids.get('other_namespace', None)  # returns None
    >>> tuples(ids.items())  # (('one_id', '1a'), ('multiple_ids', 2), ('multiple_ids', 3))

    How to add data:
    >>> ids['multiple_ids'] = 4  # TypeError
    >>> ids.add('multiple_ids', 4)  # this works
    >>> ids.update({'multiple_ids': 4})  # this works
    >>> ids.update((('multiple_ids', 4)))  # this also works
    >>> ids.update({'multiple_ids': set((4, 5))})  # this works, too
    >>> ids |= {'multiple_ids': 4} # even this works
    >>> ids |= IDs({'multiple_ids': 4}) # and this

    How to remove data:
    >>> del ids['multiple_ids']  # deletes all ids from this namespace
    >>> ids.remove('multiple_ids', 3)  # this works
    >>> ids.remove('multiple_ids', 7)  # KeyError
    >>> ids.discard('multiple_ids', 7)  # does nothing
    >>> ids.clear()  # clear completely

    How to compare:
    >>> len(ids)  # how many ids in total
    >>> ids & IDs({'multiple_ids': 3})  # returns IDs({'multiple_ids': 3})
    >>> ids & IDs({'multiple_ids': 9})  # returns IDs({})
    >>> if ids & IDs({'multiple_ids': 9}):
    ...     pass  # this gets executed if there are common ids
    """
    def __init__(self, initialdata={}):
        """
        Initialize the IDs object.
        Works exactly like initializing a dict – initialdata can be dict or a iterable of 2-tuples.

        There are two ways to give multiple ids:
        >>> ids = IDs((('one_id', '1a'), ('multiple_ids', 2), ('multiple_ids', 3)))
        >>> ids = IDs({'one_id': '1a', 'multiple_ids': (2, 3)})

        """
        items = initialdata.items() if isinstance(initialdata, (dict, IDs)) else initialdata
        self.data = {name: (value if isinstance(value, (set, list, tuple)) else set((value, )))
                     for name, value in items}

    def __getitem__(self, name):
        """
        Get any ID from this namespace or raise KeyError
        """
        return next(iter(self.data[name]))

    def __setitem__(self, name):
        """
        Not supported, use .add()
        """
        raise TypeError('Use IDs.add()')

    def __delitem__(self, name):
        """
        Delete all IDs from this namespace
        """
        del self.data[name]

    def __contains__(self, name):
        """
        Check if any ids from this namespace are contained
        """
        return name in self.data

    def __iter__(self):
        """
        Iterate over namespaces
        """
        return iter(self.data)

    def clear(self):
        """
        Clear data
        """
        self.data = {}

    def copy(self):
        """
        Return a copy
        """
        return self.__class__(self.data)

    def keys(self):
        """
        Get namespaces
        """
        return self.data.keys()

    def add(self, name, value):
        """
        Add id to namespace
        """
        self.data.setdefault(name, set()).add(value)

    def remove(self, name, value):
        """
        Remove id from namespace.
        Raises KeyError if the namespace did no exist and ValueError if the id did not exist.
        """
        self.data[name].remove(value)
        if not self.data[name]:
            del self.data[name]

    def discard(self, name, value):
        """
        Remove id from namespace if it existed.
        """
        if name not in self.data:
            return

        self.data[name].discard(value)
        if not self.data[name]:
            del self.data[name]

    def get(self, name, default=None):
        """
        Get any id fom this namespace or the default value if there is no id from this namespace.
        """
        return self[name] if name in self.data else default

    def __len__(self):
        """
        Get total count of ids
        """
        return sum((len(values) for values in self.data.values()), 0)

    def getall(self, name):
        """
        Get all ids from this namespace.
        """
        return frozenset(self.data.get(name, set()))

    def items(self):
        """
        Iterate over (namespace, id) tuples.
        """
        for name, values in self.data.items():
            for value in values:
                yield name, value

    def values(self):
        """
        Iterate over all ids.
        """
        return (value for name, value in self.items())

    def update(self, other):
        """
        Update ids using dictionary, iterable or other IDs object.
        """
        for name, value in other.items():
            self.data.setdefault(name, set()).update(value if isinstance(value, (set, list, tuple)) else set(value))

    def serialize(self):
        return {name: (tuple(values) if len(values)-1 else next(iter(values)))
                for name, values in self.data.items() if values}

    def union(self, other):
        """
        Return new IDs object with IDs from this and the other object combined.
        """
        result = self.copy()
        result.update(other)
        return result

    def intersection(self, other):
        """
        Return new IDs object with IDs that are both in this and the other object.
        """
        return self.__class__(set(self.items()) & set(self.__class__(other).items()))

    __and__ = intersection
    __or__ = union
    __ior__ = update

    @classmethod
    def unserialize(self, data):
        return self.__class__(data)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.data)


class FrozenIDs(IDs):
    """
    Like IDs, but can not be altered. Use IDs(frozenids) to get a alterable version.
    """
    def _frozen_error(self, *args, **kwargs):
        raise TypeError('FrozenIDs can not be altered')

    add = _frozen_error
    __delitem__ = _frozen_error
    remove = _frozen_error
    clear = _frozen_error
    discard = _frozen_error
    update = _frozen_error
    __ior__ = _frozen_error


class IFOPT(Serializable):
    @classmethod
    def parse(cls, string):
        if string is None:
            return None

        try:
            return cls(*string.split(':'))
        except TypeError:
            # Wrong number of arguments
            return None

    def __str__(self):
        return ':'.join(self)

    def serialize(self):
        return str(self)

    @classmethod
    def unserialize(cls, data):
        return cls.parse(data)


class StopIFOPT(IFOPT, namedtuple('StopIFOPT', ('country', 'area', 'stop'))):
    pass


class StopAreaIFOPT(IFOPT, namedtuple('StopAreaIFOPT', ('country', 'area', 'stop', 'level'))):
    def get_stop_ifopt(self):
        return StopIFOPT(*self[:3])


class PlatformIFOPT(IFOPT, namedtuple('PlatformIFOPT', ('country', 'area', 'stop', 'level', 'quay'))):
    def get_area_ifopt(self):
        return StopAreaIFOPT(*self[:4])

    def get_stop_ifopt(self):
        return StopIFOPT(*self[:3])
