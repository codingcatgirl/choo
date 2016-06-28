from choo.types import PlatformIFOPT, StopAreaIFOPT, StopIFOPT


class TestIFOPT:
    ifopt = PlatformIFOPT('1', '2', '3', '4', '5')

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
