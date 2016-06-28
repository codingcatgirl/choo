import pytest

from choo.types import Coordinates


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
