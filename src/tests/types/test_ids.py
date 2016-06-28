import pytest

from choo.types import FrozenIDs, IDs, PlatformIFOPT, StopAreaIFOPT, StopIFOPT


class TestIDs:
    ids = IDs((('one', '1a'), ('multiple', 2), ('multiple', 3)))

    def test_init(self):
        assert set(self.ids.items()) == set((('one', '1a'), ('multiple', 2), ('multiple', 3)))

    def test_getitem(self):
        assert self.ids['one'] == '1a'
        assert self.ids['multiple'] in (2, 3)
        with pytest.raises(KeyError):
            self.ids['unknown']

    def test_setitem(self):
        with pytest.raises(AttributeError):
            self.ids['one'] = 42

    def test_delitem(self):
        ids = self.ids.copy()
        del ids['one']
        assert 'one' not in ids
        with pytest.raises(KeyError):
            del ids['one']

    def test_contains(self):
        assert 'one' in self.ids
        assert 'unknown' not in self.ids

    def test_iter(self):
        assert set(self.ids) == {'one', 'multiple'}

    def test_clear(self):
        ids = self.ids.copy()
        ids.clear()
        assert len(ids) == 0

    def test_copy(self):
        ids = self.ids.copy()
        assert len(ids) == len(self.ids)
        assert set(ids) == set(self.ids)
        assert set(ids.items()) == set(self.ids.items())
        assert self.ids.data['one'] is not ids.data['one']
        assert self.ids.data['multiple'] is not ids.data['multiple']

    def test_keys(self):
        assert set(self.ids.keys()) == {'one', 'multiple'}

    def test_add(self):
        ids = self.ids.copy()
        ids.add('one', 10)
        assert ('one', 10) in ids.items()

    def test_remove(self):
        assert set(self.ids.items()) == set((('one', '1a'), ('multiple', 2), ('multiple', 3)))
        ids = self.ids.copy()
        with pytest.raises(KeyError):
            ids.remove('unknown', 1)
        with pytest.raises(KeyError):
            ids.remove('one', 'unknown')
        ids.remove('one', '1a')
        assert ('one', '1a') not in ids.items()
        assert 'one' not in ids
        assert ('multiple', 2) in list(ids.items())
        ids.remove('multiple', 2)
        assert ('multiple', 2) not in ids.items()
        assert ('multiple', 3) in ids.items()

    def test_discard(self):
        ids = self.ids.copy()
        ids.discard('unknown', 1)
        ids.discard('one', 'unknown')
        ids.discard('one', '1a')
        assert ('one', '1a') not in ids.items()
        assert 'one' not in ids
        ids.discard('multiple', 2)
        assert ('multiple', 2) not in ids.items()
        assert ('multiple', 3) in ids.items()

    def test_get(self):
        assert self.ids.get('one') == '1a'
        assert self.ids.get('multiple') in (2, 3)
        assert self.ids.get('unknown') is None

    def test_len(self):
        ids = self.ids.copy()
        assert len(ids) == 3
        ids.discard('one', '1a')
        assert len(ids) == 2

    def test_getall(self):
        assert isinstance(self.ids.getall('one'), frozenset)
        assert self.ids.getall('one') == {'1a'}
        assert self.ids.getall('multiple') == {2, 3}
        assert self.ids.getall('unknown') == set()

    def test_values(self):
        assert set(self.ids.values()) == {'1a', 2, 3}

    def test_update(self):
        ids = IDs()
        ids.update((('one', '1a'), ('multiple', 2), ('multiple', 3)))
        assert len(ids & self.ids) == 3

        ids = IDs()
        ids.update({'one': '1a', 'multiple': (2, 3)})
        assert len(ids & self.ids) == 3

        ids = IDs()
        ids.update({'one': '1a', 'multiple': {2, 3}})
        assert len(ids & self.ids) == 3

        ids = IDs()
        ids.update({'one': '1a', 'multiple': [2, 3]})
        assert len(ids & self.ids) == 3

        ids = IDs()
        ids.update(IDs({'one': '1a', 'multiple': (2, 3)}))
        assert len(ids & self.ids) == 3

        ids = self.ids.copy()
        ids.update({'new': {1}, 'one': {2, 3}, 'multiple': 4})
        assert set(ids.items()) == {('new', 1), ('one', '1a'), ('one', 2), ('one', 3),
                                    ('multiple', 2), ('multiple', 3), ('multiple', 4)}

    def test_serialize(self):
        assert self.ids.serialize() in ({'one': '1a', 'multiple': (2, 3)}, {'one': '1a', 'multiple': (3, 2)})

    def test_union(self):
        ids = IDs()
        ids |= (('one', '1a'), ('multiple', 2), ('multiple', 3))
        assert len(ids & self.ids) == 3

    def test_intersection(self):
        intersection = self.ids & (('one', '1a'), ('new', 4), ('multiple', 3))
        assert set(intersection.items()) == {('one', '1a'), ('multiple', 3)}

    def test_unserialize(self):
        assert len(IDs.unserialize(self.ids.serialize()) & self.ids) == 3

    def test_frozen(self):
        ids = FrozenIDs(self.ids)

        with pytest.raises(TypeError):
            ids.add('multiple', 4)

        with pytest.raises(TypeError):
            del ids['multiple']

        with pytest.raises(TypeError):
            ids.remove('multiple', 2)

        with pytest.raises(TypeError):
            ids.clear()

        with pytest.raises(TypeError):
            ids.discard('multiple', 2)

        with pytest.raises(TypeError):
            ids.update({})

    def test_repr(self):
        assert len(eval(repr(self.ids)) & self.ids) == 3


class TestIFOPT:
    ifopt = PlatformIFOPT('1', '2', '3', '4', '5')

    def test_init_none(self):
        assert PlatformIFOPT.parse(None) is None

    def test_init_arguments_count(self):
        assert PlatformIFOPT.parse('1:2') is None

    def test_parse(self):
        assert PlatformIFOPT.parse('1:2:3:4:5') == self.ifopt

    def test_serializable(self):
        assert PlatformIFOPT.unserialize('1:2:3:4:5') == self.ifopt
        assert self.ifopt.serialize() == '1:2:3:4:5'

    def test_get_sub_ids(self):
        assert self.ifopt.get_area_ifopt() == StopAreaIFOPT('1', '2', '3', '4')
        assert self.ifopt.get_stop_ifopt() == StopIFOPT('1', '2', '3')
        assert self.ifopt.get_area_ifopt().get_stop_ifopt() == StopIFOPT('1', '2', '3')

    def test_str(self):
        assert str(self.ifopt) == '1:2:3:4:5'
