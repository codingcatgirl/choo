import pytest

from choo.types import LineType, LineTypes, PlatformType, POIType, WalkSpeed, WayEvent, WayType


class TestEnums:
    def test_serialize(self):
        assert WayType.walk.serialize() == 'walk'

    def test_unserialize(self):
        assert WayType.unserialize('walk') is WayType.walk
        with pytest.raises(AttributeError):
            WayType.unserialize('unknown')
        with pytest.raises(AttributeError):
            WayType.unserialize('serialize')

    def test_contains(self):
        assert WayEvent.stairs_up in WayEvent.stairs
        assert WayEvent.stairs_up in WayEvent.any
        assert WayEvent.stairs in WayEvent.any
        assert WayEvent.stairs not in WayEvent.stairs_up
        assert WayEvent.stairs not in WayEvent.down
        assert WayEvent.stairs not in WayEvent.elevator
        assert WayEvent.any not in WayEvent.up
        with pytest.raises(TypeError):
            1 in WayType.any

    def test_iter(self):
        assert set(WayEvent.stairs) == {WayEvent.stairs, WayEvent.stairs_up, WayEvent.stairs_down}

    def test_contained_in(self):
        assert set(WayEvent.up.contained_in()) == {WayEvent.up, WayEvent.any}

    def test_repr(self):
        assert repr(WayType.walk) == 'WayType.walk'
        assert repr(WayEvent.stairs) == 'WayEvent.stairs'
        assert repr(WalkSpeed.normal) == 'WalkSpeed.normal'
        assert repr(LineType.train) == 'LineType.train'
        assert repr(POIType.parking) == 'POIType.parking'
        assert repr(PlatformType.street) == 'PlatformType.street'


class TestLineTypes:
    def test_init(self):
        LineTypes(LineType.bus)
        with pytest.raises(TypeError):
            assert LineTypes(1)

    def test_contains(self):
        assert LineType.train in LineTypes.any
        assert LineType.any in LineTypes(LineType.train)
        assert LineType.bus in LineTypes(LineType.bus_regional)
        assert LineType.train not in LineTypes(LineType.bus_regional)
        with pytest.raises(TypeError):
            assert 1 in LineTypes.any

    def test_exclude(self):
        assert LineType.tram in LineTypes.any.exclude(LineType.train, LineType.bus)
        assert LineType.bus_regional not in LineTypes.any.exclude(LineType.train, LineType.bus)
        with pytest.raises(TypeError):
            assert LineTypes.any.exclude(1)

    def test_include(self):
        assert LineType.tram not in LineTypes.none.include(LineType.train, LineType.bus)
        assert LineType.bus_regional in LineTypes.none.include(LineType.train, LineType.bus)
        with pytest.raises(TypeError):
            assert LineTypes.none.include(1)

    def test_repr(self):
        linetypes = LineTypes.any.exclude(LineType.bus)
        assert set(eval(repr(linetypes))) == set(linetypes)
