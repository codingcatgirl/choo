import os
from collections import deque

from ..models.base import ModelWithIDs, SourcedModelMixin


class DefaultCache:
    def __init__(self):
        self._i = 0
        self._collection_data = {}
        self._id_collection = {}
        self._collection_referenced_by = {}
        self._collection_references = {}
        self._serialization_ids = {}

    def apply_recursive(self, *objects):
        self.add_recursive(*objects)
        return [obj._apply_recursive(self.get) for obj in objects]

    def add_recursive(self, *objects):
        for obj in objects:
            obj._call_recursive(self.add)

    def apply(self, obj):
        self.add(obj)
        return self.get(obj)

    def _get_obj_ids(self, obj):
        # find out the object id tuples (with model)
        return tuple(((obj.Model, )+id_) for id_ in obj.ids.items())

    def _get_collections(self, obj):
        if not isinstance(obj, ModelWithIDs) or not obj.ids or not isinstance(obj, SourcedModelMixin):
            return None, None

        # find out collection(s) this obj belongs to
        object_ids = self._get_obj_ids(obj)
        collections = tuple(set(i for i in (self._id_collection.get(id_) for id_ in object_ids) if i is not None))
        return collections, object_ids

    def add(self, obj):
        collections, object_ids = self._get_collections(obj)
        if collections is None:
            return None

        obj = obj.sourced()
        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('\nGot object for cache:', obj)

        # if it belongs to no collection, create new collection and add it
        if not collections:
            if os.environ.get('CHOO_CACHE_DEBUG'):
                print('This is a new object!')
            collection = self._i
            self._i += 1

            # add the data, the ids, and start refer-lists
            self._collection_data[collection] = obj
            for id_ in object_ids:
                self._id_collection[id_] = collection
            self._collection_referenced_by[collection] = set()
            self._collection_references[collection] = set()

            # now we have to check the references
            for name in obj._nonproxy_fields:
                value = getattr(obj, name)
                added = self.get_or(value)
                if not added:
                    continue
                obj._data[name] = added
                c = self._get_collections(value)[0][0]
                if os.environ.get('CHOO_CACHE_DEBUG'):
                    print('it refers to known object:', self._collection_data[c])
                self._collection_referenced_by[c].add(collection)
                self._collection_references[collection].add(c)
            return obj

        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('it belongs to %d collection(s)' % len(collections))

        # add new object to the first collection that matches
        collection = collections[0]
        updated_obj = self._update_collection(collection, obj)

        # merge all other matching collections into the first one
        for c in collections[1:]:
            # get old collection data for the end
            old_collection_data = self._collection_data[c]
            del self._collection_data[c]

            # delete all references
            for c_ in self._collection_references[c]:
                self._collection_referenced_by[c_].discard(c)
            del self._collection_referenced_by[c]

            updated_obj = self._update_collection(collection, old_collection_data)

        return updated_obj

    def _update_collection(self, collection, obj, noupdate=None):
        # update ids for this collection
        for id_ in self._get_obj_ids(obj):
            self._id_collection[id_] = collection

        # what this method does is merge objects recursively. so, if we merge two stops (who describe the same stop),
        # it merges also the city objects, even if they have no common ids (same stop means same city).
        oldobj = self._collection_data[collection]
        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('update collection', oldobj)

        # we build a new object with the merged attributes
        kwargs = {}
        for name, value in obj._data.items():
            # only handle MdoelWithIDs attributes because only they are mergeable
            value = getattr(obj, name)
            if value is None:
                continue
            oldvalue = getattr(oldobj, name)
            if oldvalue is None or not isinstance(value, ModelWithIDs):
                kwargs[name] = value
                continue

            # which collection describes (and described) this value?
            value_collection = self._get_collections(oldvalue)[0][0]

            # merge the value
            if oldvalue is not value:
                if os.environ.get('CHOO_CACHE_DEBUG'):
                    print('its', name, 'attribute has to be updated, too')
                kwargs[name] = self._update_collection(value_collection, value, noupdate=collection)

            # update the references
            self._collection_referenced_by[value_collection].add(collection)
            self._collection_references[collection].add(value_collection)

        self._collection_data[collection] = self._collection_data[collection] | obj.Model.Sourced(**kwargs)

        # now we look, which collection refer to this collection. those have to be updated, to point to the new data
        for other_collection in self._collection_referenced_by[collection]:
            if other_collection is not noupdate:
                if os.environ.get('CHOO_CACHE_DEBUG'):
                    print('we now have to update', self._collection_data[other_collection], 'because it referred')
                self._update_collection(other_collection, self._collection_data[other_collection])

        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('done updating')

        return self._collection_data[collection]

    def get(self, obj):
        return self.get_or(obj, obj)

    def get_or(self, obj, default=None):
        collections, object_ids = self._get_collections(obj)
        if not collections:
            return default
        return self._collection_data[collections[0]]

    def create_serialization_ids(self):
        self._serialization_ids = {}
        objects = deque()
        for i, (collection, obj) in enumerate(self._collection_data.items()):
            self._serialization_ids[collection] = i
            objects.append(obj)
        return tuple(objects)

    def get_serialization_id(self, obj):
        return self._serialization_ids[self._id_collection[self._get_obj_ids(obj)[0]]]
