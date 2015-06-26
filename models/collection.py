#!/usr/bin/env python3
from .base import Serializable, Collectable


class Collection(Serializable):
    def __init__(self):
        self.known = {}
        self.by_id = {}
        self.by_pid = {}

    def _serialize(self):
        return {model: [obj.serialize() for obj in objects] for model, objects in self.known.items()}

    def _get_lists(self, obj):
        name = obj._serialized_name()
        if name not in self.known:
            self.known[name] = obj.Results()
            self.by_id[name] = {}
        return self.known[name], self.by_id[name]

    def retrieve(self, obj):
        assert isinstance(obj, Collectable)

        model = obj._serialized_name()
        by_id = self.by_id.get(model)
        if not by_id:
            return

        if id(obj) in self.by_pid:
            return self.by_pid[id(obj)]

        for name, value in obj._ids.items():
            found = by_id.get(name, {}).get(value)
            if found is not None:
                if model == 'Ride' and found != obj:
                    continue
                return found

        if model == 'Platform' and obj.name is None and obj.full_name is None:
            return

        for item in self.known.get(model):
            for name in obj._ids:
                if name in item._ids:
                    break
            else:
                if item == obj:
                    return item

    def add(self, obj):
        model = obj._serialized_name()
        if model == 'Platform' and obj.name is None and obj.full_name is None:
            return obj

        found = self.retrieve(obj)
        is_new = False
        if found is not None:
            if found is obj:
                return found
            found.update(obj)
        else:
            found = obj
            self.by_pid[id(found)] = found
            is_new = True

        ids = {name: value for name, value in obj._ids.items() if type(value) != tuple or None not in value}
        if model not in self.by_id:
            self.by_id[model] = {name: {value: found} for name, value in ids.items()}
            self.known[model] = obj.Results([found])
        else:
            by_id = self.by_id[model]
            for name, value in ids.items():
                if name not in by_id:
                    by_id[name] = {}
                by_id[name][value] = found

        if is_new:
            self.known[model].append(found)

        return found
