import os
from collections import deque

from ..models.base import ModelWithIDs, SourcedModelMixin


class CacheItem:
    def __init__(self, cache, obj):
        self.cache = cache
        self.obj = obj.sourced()
        self.referenced_by = set()
        self.references = set()
        self.ids = set(((obj.Model, )+id_) for id_ in obj.ids.items())
        self.i = None

    def add_to_cache(self):
        if self.i is not None:
            raise TypeError('Item was already added to cache!')

        # add the data, the ids, and start refer-lists
        self.i = len(self.cache._items)
        self.cache._items.append(self)
        for id_ in self.ids:
            self.cache._items_by_id[id_] = self

        # now we have to check the references
        for name in self.obj._nonproxy_fields:
            value = getattr(self.obj, name)
            found_item = self.cache.get_item_or(value)
            if not found_item:
                continue
            self.obj._data[name] = found_item.obj
            self.references.add(found_item)
            found_item.referenced_by.add(self)

    def remove_from_cache(self):
        if self.i is None:
            raise TypeError('Item is not added to cache!')

        # remove item from cache
        if len(self.cache._items) > 1:
            lastitem = self.cache.pop()
            self.cache._items[self.i] = lastitem
            lastitem.i = self.i
        else:
            self.cache._items = []

        # delete all references
        for item in self.references:
            item.referenced_by.discard(self)
        for item in self.referenced_by:
            item.references.discard(self)

    def update(self, other, noupdate=None):
        if self.i is None:
            raise TypeError('Item is not added to cache!')

        # update ids for this collection
        for id_ in other.ids:
            self.cache._items_by_id[id_] = self

        # what this method does is merge objects recursively. so, if we merge two stops (who describe the same stop),
        # it merges also the city objects, even if they have no common ids (same stop means same city).
        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('update collection', self.obj)

        # we build a new object with the merged attributes
        kwargs = {}
        for name, value in other.obj._data.items():
            # only handle MdoelWithIDs attributes because only they are mergeable
            value = getattr(other.obj, name)
            if value is None:
                continue
            oldvalue = getattr(self.obj, name)
            if oldvalue is None or not isinstance(value, ModelWithIDs):
                kwargs[name] = value
                continue

            # which collection describes (and described) this value?
            value_item = self.cache.get_item_or(oldvalue)

            # merge the value
            if oldvalue is not value:
                if os.environ.get('CHOO_CACHE_DEBUG'):
                    print('its', name, 'attribute has to be updated, too')
                kwargs[name] = value_item.update(self.cache._newitem(value), noupdate=self).obj

            # update the references
            value_item.referenced_by.add(self)
            self.references.add(value_item)

        self.obj = self.obj | self.obj.Model.Sourced(**kwargs)

        # now we look, which collection refer to this collection. those have to be updated, to point to the new data
        for other_item in self.referenced_by:
            if other_item is not noupdate:
                if os.environ.get('CHOO_CACHE_DEBUG'):
                    print('we now have to update', other_item.obj, 'because it referred')
                other_item.update(other_item)

        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('done updating')

        return self


class DefaultCache:
    def __init__(self):
        self._i = 0
        self._items = []
        self._items_by_id = {}

    def apply(self, *objects):
        self.add_recursive(*objects)
        return [obj._apply_recursive(self.get) for obj in objects]

    def add_recursive(self, *objects):
        for obj in objects:
            obj._call_recursive(self.add)

    def _get_same_items(self, item):
        return set(i for i in (self._items_by_id.get(id_) for id_ in item.ids) if i is not None)

    def _newitem(self, obj):
        if not isinstance(obj, ModelWithIDs) or not obj.ids or not isinstance(obj, SourcedModelMixin):
            return None
        return CacheItem(self, obj)

    def add(self, obj):
        newitem = self._newitem(obj)
        if newitem is None:
            return None

        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('\nGot object for cache:', newitem.obj)

        same_items = self._get_same_items(newitem)

        # if it belongs to no collection, create new collection and add it
        if not same_items:
            if os.environ.get('CHOO_CACHE_DEBUG'):
                print('This is a new object!')

            newitem.add_to_cache()
            return newitem.obj

        if os.environ.get('CHOO_CACHE_DEBUG'):
            print('it belongs to %d collection(s)' % len(same_items))

        # add new object to the first collection that matches
        item = same_items.pop()
        item.update(newitem)

        # merge all other matching collections into the first one
        for same_item in same_items:
            same_item.remove_from_cache()
            item.update(same_item)

        return item.obj

    def get(self, obj):
        return self.get_or(obj, obj)

    def get_or(self, obj, default=None):
        item = self._newitem(obj)
        if item is None:
            return default
        same_items = self._get_same_items(item)
        if not same_items:
            return default
        return next(iter(same_items)).obj

    def get_item_or(self, obj, default=None):
        item = self._newitem(obj)
        if item is None:
            return default
        same_items = self._get_same_items(item)
        if not same_items:
            return default
        return next(iter(same_items))

    def create_serialization_ids(self):
        self._serialization_ids = {}
        objects = deque()
        for i, (collection, obj) in enumerate(self._collection_data.items()):
            self._serialization_ids[collection] = i
            objects.append(obj)
        return tuple(objects)

    def get_serialization_id(self, obj):
        return self._serialization_ids[self._id_collection[self._get_obj_ids(obj)[0]]]
