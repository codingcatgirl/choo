import pytest

from choo.apis import vrr
from choo.models import Stop
from choo.types import Coordinates


class TestQuery:
    def test_fields(self):
        query = vrr.stops.where(city__name='Essen', coords=Coordinates(51.462983, 6.956251))
        assert query.city__name == 'Essen'

        with pytest.raises(TypeError):
            query.name = 'bla'
        with pytest.raises(TypeError):
            del query.name

    def test_settings(self):
        query = vrr.stops
        assert query.max_distance(500).settings.max_distance == 500
        assert query.limit(10).settings.limit == 10

        with pytest.raises(AttributeError):
            query.settings.whatever
        with pytest.raises(TypeError):
            query.settings.limit = 7
        with pytest.raises(TypeError):
            del query.settings.limit
        with pytest.raises(TypeError):
            query.name = 'bla'
        with pytest.raises(TypeError):
            del query.name

    def test_serialization(self):
        serialized = {
            "@type": "location.query",
            "api": "vrr",
            "obj": {
                "@type": "location",
                "name": "Essen Rathaus"
            },
            "settings": {
                "limit": 10,
                "max_distance": 1000
            }
        }
        assert vrr.locations.where(name='Essen Rathaus').limit(10).serialize() == serialized
        # assert Serializable.unserialize(serialized).serialize() == serialized

    def test_iter(self):
        query = vrr.stops
        results = (Stop(city__name='Essen', name='Hauptbahnhof'), )
        query.set_results_generator(results)
        assert tuple(query) == results
        assert tuple(query) == results
