import pytest

from choo.models import Model
from choo.types import Coordinates, LineType


class TestCoordinates:
    def test_distance(self):
        assert round(Coordinates(51.451379, 7.013569).distance_to(Coordinates(51.454726, 6.979494)), 3) == 2390.268
        with pytest.raises(TypeError):
            Coordinates(51.451379, 7.013569).distance_to(7)

    def test_serialize(self):
        assert tuple(Coordinates(51.451379, 7.013569).serialize()) == (51.451379, 7.013569)

    def test_unserialize(self):
        assert Coordinates(51.451379, 7.013569) == Coordinates.unserialize((51.451379, 7.013569))

    def test_reversed(self):
        assert reversed(Coordinates(51.451379, 7.013569)) == (7.013569, 51.451379)


class TestSerializable:
    def test_no_serialize_supported(self):
        model = Model()
        with pytest.raises(TypeError):
            model.serialize()

    def test_wrong_type(self):
        with pytest.raises(ValueError):
            Model.unserialize({'@type': 'coordinates'})


class TestSimpleSerializable:
    def test_unsimple_serialize(self):
        assert LineType.train.serialize(simple=False) == {'@type': 'linetype', 'value': 'train'}

    def test_unsimple_unserialize(self):
        assert LineType.unserialize({'@type': 'linetype', 'value': 'train'}) == LineType.train
        with pytest.raises(ValueError):
            LineType.unserialize({'@type': 'stop'})
