from datetime import datetime

import pytest

from choo.apis import vrr
from choo.models import City, Stop
from choo.models.base import SourcedModelMixin


class TestModel:
    def test_init(self):
        assert Stop(name='Essen Hbf').name == 'Essen Hbf'
        assert Stop(city__name='Essen').city__name == 'Essen'
        with pytest.raises(AttributeError):
            Stop(invalid_field='Essen')
        with pytest.raises(TypeError):
            Stop(city=27)

    def test_serializing(self):
        serialized = {
            '@type': 'stop',
            'name': 'Essen Hbf',
        }
        assert Stop(name='Essen Hbf').serialize() == serialized
        assert Stop.unserialize(serialized).serialize() == serialized

        with pytest.raises(AttributeError):
            Stop.unserialize({
                '@type': 'stop',
                'invalid_field': 'Essen',
            })


class TestSourcedModelMixin:
    sourced_city = City.unserialize({
        "@type": "city.sourced",
        "source": "vrr",
        "time": "2016-07-02T12:33:50",
        "country": "de",
        "state": "nrw",
        "official_id": "05113000",
        "name": "Essen",
        "ids": {
            "@type": "ids.frozen",
            "vrr": "placeID:5113000:18"
        }
    })

    def test_init(self):
        with pytest.raises(TypeError):
            SourcedModelMixin()

        assert self.sourced_city.source == vrr
        assert self.sourced_city.time == datetime(2016, 7, 2, 12, 33, 50)

    def test_from_parser(self):
        with pytest.raises(TypeError):
            SourcedModelMixin()

        with pytest.raises(ValueError):
            Stop.Sourced.from_parser(City)

    def test_mutable(self):
        assert self.sourced_city.mutable().serialize() == {
            "@type": "city",
            "country": "de",
            "state": "nrw",
            "official_id": "05113000",
            "name": "Essen",
            "ids": {
                "@type": "ids.frozen",
                "vrr": "placeID:5113000:18"
            }
        }

    def test_immutable(self):
        with pytest.raises(TypeError):
            self.sourced_city.name = 'Duisburg'

        with pytest.raises(TypeError):
            del self.sourced_city.name

    def test_custom_properties(self):
        self.sourced_city.choo_testing_property = 42
        assert self.sourced_city.choo_testing_property == 42
        del self.sourced_city.choo_testing_property
        with pytest.raises(AttributeError):
            self.sourced_city.choo_testing_property


class TestModelWithIDs:
    city1 = {
        "@type": "city",
        "country": "de",
        "state": "nrw",
        "official_id": "05113000",
        "name": "Essen",
        "ids": {
            "@type": "ids.frozen",
            "vrr": "placeID:5113000:18"
        }
    }
    city2 = {
        "@type": "city",
        "country": "de",
        "state": "nrw",
        "official_id": "05112000",
        "name": "Duisburg",
        "ids": {
            "@type": "ids.frozen",
            "vrr": "placeID:5112000:20"
        }
    }

    def test_eq(self):
        assert (City.unserialize(self.city1) == City.unserialize(self.city1)) is True
        assert (City.unserialize(self.city1) == City.unserialize(self.city2)) is None
        assert (City.unserialize(self.city1) == Stop()) is False
        assert (City.unserialize(self.city1) == 42) is False
