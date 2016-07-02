# flake8: noqa
from choo.types import Serializable


class TestOdvNameElemStop:
    def test_base(self):
        query = Serializable.unserialize({
            '@type': 'stop.parser.efa.parsers.odvOdvNameElemStop',
            'api': 'vrr',
            'time': '2016-07-02T12:33:50',
            'data': '''
                <odvNameElem anyType="stop" buildingName="" buildingNumber="" choo-text="Essen, Borbeck Süd Bahnhof" gid="de:5113:9159" id="20009159" locality="Essen" mainLocality="Essen" mapName="WGS84" nameKey="" objectName="Borbeck Süd Bahnhof" omc="5113000" placeID="18" postCode="" stateless="20009159" streetName="" x="6954254" y="51462987">
                    Essen, Borbeck Süd Bahnhof
                    <odvPlaceElem mainPlace="1" omc="5113000" placeID="18" span="0" stateless="placeID:5113000:18" type="remote" value="5113000:18">Essen</odvPlaceElem>
                </odvNameElem>
                ''',
            'kwargs': {},
        })
        assert query.sourced().serialize() == {
            "@type": "stop.sourced",
            "source": "vrr",
            "time": "2016-07-02T12:33:50",
            "ifopt": "de:5113:9159",
            "city": {
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
            },
            "name": "Borbeck Süd Bahnhof",
            "coords": [
                51.462987,
                6.954254
            ],
            "ids": {
                "@type": "ids.frozen",
                "vrr": "20009159"
            }
        }
