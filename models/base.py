#!/usr/bin/env python3


class Serializable():
    def serialize(self):
        return self.__dict__


class ModelBase(Serializable):
    class Request(Serializable):
        pass

    class Results(Serializable):
        def __init__(self, results=[], subject=None, api=None, method=None):
            super().__init__()
            self.subject = subject
            self.api = api
            self.method = method
            self.results = tuple(results)

        def _load(self, data):
            super()._load(data)
            self._serial_get(data, 'results')
            results = self.results
            self.results = []
            for result in results:
                if type(result) in (tuple, list):
                    self.results.append((ModelBase.unserialize(result[0]), result[1]))
                else:
                    self.results.append(ModelBase.unserialize(result))
            self._serial_get(data, 'subject')
            self._serial_get(data, 'api')
            self._serial_get(data, 'method')

        def _serialize(self, ids):
            data = {}
            self._serial_add(data, 'subject', ids)
            self._serial_add(data, 'api', ids)
            self._serial_add(data, 'method', ids)
            if type(self.results[0]) == tuple:
                results = [(item[0].serialize(ids), item[1]) for item in self.results]
            else:
                results = [item.serialize(ids) for item in self.results]
            self._serial_add(data, 'results', ids, val=results)
            return data

        def __iter__(self):
            for result in self.results:
                yield result

        def __getitem__(self, key):
            return self.results[key]

    def __init__(self):
        self._ids = {}
        self._raws = {}



    @classmethod
    def load(cls, data):
        obj = cls()
        obj._load(data)
        return obj

    def _load(self, data):
        self._serial_get(data, '_ids')
        self._serial_get(data, '_raws')

    @classmethod
    def unserialize(cls, data):
        if data is None:
            return None
        if type(data) not in (list, tuple):
            return data
        mytype, data = data
        if mytype is None:
            return data
        elif mytype == 'datetime':
            return datetime.strptime(data, '%Y-%m-%d %H:%M')
        elif mytype == 'timedelta':
            return timedelta(seconds=data)
        elif mytype == 'tuple':
            return tuple(data)
        elif mytype == 'list':
            return data
        else:
            return globals()[mytype].load(data)

    def serialize(self, ids=None):
        if ids is None:
            ids = []
        myid = id(self)
        if len(ids) != len(set(ids)):
            return {}
        data = {}
        classes = self.__class__.__mro__
        newids = ids+[myid]
        for oneclass in classes:
            if hasattr(oneclass, '_serialize'):
                olddata = data
                newdata = oneclass._serialize(self, newids)
                if type(newdata) != dict and not data:
                    data = newdata
                    break
                data = newdata
                data.update(olddata)

        if myid in ids:
            data['is_truncated'] = True
        return (self.__class__.__name__, data)

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, '_ids', ids)
        if 'noraws' not in ids:
            self._serial_add(data, '_raws', ids)
        return data

    def _serial_add(self, data, name, ids, **kwargs):
        if 'val' in kwargs:
            val = kwargs['val']
        else:
            val = getattr(self, name)
            if val is None:
                return
        if isinstance(val, ModelBase):
            data[name] = val.serialize(ids)
        elif isinstance(val, datetime):
            data[name] = ('datetime', val.strftime('%Y-%m-%d %H:%M'))
        elif isinstance(val, timedelta):
            data[name] = ('timedelta', val.total_seconds())
        elif type(val) == list:
            data[name] = ('list', val)
        elif type(val) == tuple:
            data[name] = ('tuple', val)
        else:
            data[name] = val

    def _serial_get(self, data, name):
        if name in data:
            setattr(self, name, ModelBase.unserialize(data[name]))
