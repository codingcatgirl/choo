from ..models.base import Model, ModelWithIDs


class DefaultCache:
    def __init__(self):
        self._models = {}

    def apply_recursive(self, *objects):
        for obj in objects:
            obj._call_recursive(self.add)
        return [obj._apply_recursive(self.get) for obj in objects]

    def _get_cache(self, obj):
        return self._models.setdefault(obj.Model, ModelCache())

    def apply(self, obj):
        return self._get_cache(obj).apply(obj)

    def add(self, obj):
        if not isinstance(obj, ModelWithIDs):
            if not isinstance(obj, Model):
                raise TypeError('%s is not a model!' % repr(obj))
            return
        self._get_cache(obj).add(obj)

    def get(self, obj):
        if not isinstance(obj, ModelWithIDs):
            if not isinstance(obj, Model):
                raise TypeError('%s is not a model!' % repr(obj))
            return obj
        return self._get_cache(obj).get(obj)


class ModelCache:
    def __init__(self):
        self._i = 0
        self._collection_data = {}
        self._id_collection = {}
        self._by_python_id = {}

    def apply(self, obj):
        self.add(obj)
        return self.get(obj)

    def add(self, obj):
        if obj.ids is None:
            return

        # find out collection(s) this obj belongs to
        object_ids = set(obj.ids.items())
        collections = tuple(set(i for i in (self._id_collection.get(id_) for id_ in object_ids) if i is not None))

        # if it belongs to no collection, create new collection and add it
        if not collections:
            self._collection_data[self._i] = obj.sourced()
            for id_ in object_ids:
                self._id_collection[id_] = self._i
            self._i += 1
            return

        # add now model to the first collection that matches
        collection = collections[0]
        self._collection_data[collection] |= obj

        # merge all other matching collections into the first one
        for c in collections[1:]:
            self._collection_data[collection] |= self._collection_data[c]
            for id_ in self._collection_data[c].ids.items():
                self._id_collection[id_] = collection
            del self._collection_data[c]

    def get(self, obj):
        return self._collection_data[self._id_collection[tuple(obj.ids.items())[0]]]
