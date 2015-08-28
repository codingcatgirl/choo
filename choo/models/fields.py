#!/usr/bin/env python3
from collections import Iterable
from datetime import datetime, timedelta


class Field():
    _i = 0

    def __init__(self, type_, none=True):
        self.type = type_
        self.i = Field._i
        Field._i += 1
        self.none = none

    def validate(self, value):
        if self.none and value is None:
            return True
        return isinstance(value, self.type)

    def serialize(self, value):
        return value

    def unserialize(self, value):
        assert isinstance(value, self.type)
        return value


class Any(Field):
    def __init__(self, none=True):
        super().__init__(None, none)

    def validate(self, value):
        return True

    def serialize(self, value):
        return value

    def unserialize(self, value):
        return value


class DateTime(Field):
    def __init__(self, none=True):
        super().__init__(None, none)

    def validate(self, value):
        if self.none and value is None:
            return True
        return isinstance(value, datetime)

    def serialize(self, value):
        if self.none and value is None:
            return None
        return value.strftime('%Y-%m-%d %H:%M:%S')

    def unserialize(self, value):
        if self.none and value is None:
            return None
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


class Timedelta(Field):
    def __init__(self, none=True):
        super().__init__(None, none)

    def validate(self, value):
        if self.none and value is None:
            return True
        return isinstance(value, timedelta)

    def serialize(self, value):
        if self.none and value is None:
            return None
        return int(value.total_seconds())

    def unserialize(self, value):
        if self.none and value is None:
            return None
        return timedelta(seconds=value)


class Model(Field):
    _waiting = {}
    _models = {}

    def __init__(self, type_, none=True):
        super().__init__(type_, none)
        if isinstance(type_, str):
            if type_ in Model._models:
                type_ = Model._models[type_]
            else:
                if type_ not in Model._waiting:
                    Model._waiting[type_] = [self]
                else:
                    Model._waiting[type_].append(self)
        self.type = type_

    @classmethod
    def add_model(self, model):
        name_ = model._serialized_name()
        if name_ in Model._models:
            return
        Model._models[name_] = model
        if name_ in Model._waiting:
            for field in Model._waiting[name_]:
                field.type = model
            del Model._waiting[name_]

    def validate(self, value):
        if self.none and value is None:
            return True
        assert isinstance(value, self.type)
        return value.validate()

    def serialize(self, value):
        if self.none and value is None:
            return None
        return self.type.serialize(value)

    def unserialize(self, value):
        if self.none and value is None:
            return None
        return self.type.unserialize(value)


class List(Field):
    def __init__(self, type_, none=False, set_=False):
        super().__init__(type_, none)
        self.type = type_
        self.set = set_

    def validate(self, value):
        if self.none and value is None:
            return True
        assert isinstance(value, Iterable if not self.set else set)
        for item in value:
            assert self.type.validate(item)
        return True

    def serialize(self, value):
        if self.none and value is None:
            return None
        return [self.type.serialize(item) for item in value]

    def unserialize(self, value):
        if self.none and value is None:
            return None
        if self.set:
            return set([self.type.unserialize(item) for item in value])
        else:
            return [self.type.unserialize(item) for item in value]


class Set(List):
    def __init__(self, field, none=True):
        super().__init__(field, none, True)


class Tuple(Field):
    def __init__(self, *types, none=False):
        super().__init__(None, none)
        self.types = types

    def validate(self, value):
        if self.none and value is None:
            return True
        assert isinstance(value, tuple)
        assert len(value) == len(self.types)
        for i, type_ in enumerate(self.types):
            assert type_.validate(value[i])
        return True

    def serialize(self, value):
        if self.none and value is None:
            return None
        return [type_.serialize(value[i]) for i, type_ in enumerate(self.types)]

    def unserialize(self, value):
        if self.none and value is None:
            return None
        return tuple([type_.unserialize(value[i]) for i, type_ in enumerate(self.types)])


class Dict(Field):
    def __init__(self, key, value, none=True):
        super().__init__(None, none)
        self.key = key
        self.value = value

    def validate(self, value):
        if self.none and value is None:
            return True
        assert isinstance(value, dict)
        for k, v in value.items():
            assert self.key.validate(k)
            assert self.value.validate(v)
        return True

    def serialize(self, value):
        if self.none and value is None:
            return None
        return {self.key.serialize(k): self.value.serialize(v) for k, v in value.items()}

    def unserialize(self, value):
        if self.none and value is None:
            return None
        return {self.key.unserialize(k): self.value.unserialize(v) for k, v in value.items()}


class RideStops(Field):
    def __init__(self):
        super().__init__(None, False)

    def validate(self, value):
        from .ride import Ride
        from .timeandplace import TimeAndPlace
        assert isinstance(value, list)
        for k, v in value.items():
            assert isinstance(k, Ride.StopPointer)
            assert v is None or isinstance(v, TimeAndPlace)
        return True

    def serialize(self, value):
        if self.none and value is None:
            return None
        return {self.key.serialize(k): self.value.serialize(v) for k, v in value.items()}

    def unserialize(self, value):
        if self.none and value is None:
            return None
        return {self.key.unserialize(k): self.value.unserialize(v) for k, v in value.items()}
