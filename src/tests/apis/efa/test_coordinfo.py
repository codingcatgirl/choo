# flake8: noqa
from choo.types import Serializable


class TestCoordInfoPlatform:
    def test_base(self):
        query = Serializable.unserialize({
            '@type': 'platform.parser.efa.parsers.coordinfoCoordInfoPlatform',
            'api': 'vrr',
            'time': '2016-07-02T12:49:39',
            'data': '''
                <coordInfoItem distance="210" gisLayer="SYS-STOPPOINT" id="20009159-3-1" locality="Essen" name="Borbeck Süd Bahnhof" omc="5113000" placeID="18" stateless="20009159-3-1" type="BUS_POINT">
                    <itdPathCoordinates>
                        <coordEllipsoid>WGS84</coordEllipsoid>
                        <coordType>GEO_DECIMAL</coordType>
                        <itdCoordinateBaseElemList>
                            <itdCoordinateBaseElem>
                                <x>6954362</x>
                                <y>51462965</y>
                            </itdCoordinateBaseElem>
                        </itdCoordinateBaseElemList>
                    </itdPathCoordinates>
                    <genAttrList>
                        <genAttrElem>
                            <name>STOP_POINT_LONGNAME</name>
                            <value/>
                        </genAttrElem>
                        <genAttrElem>
                            <name>STOP_POINT_CHARACTERISTICS</name>
                            <value>Bay</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>STOP_POINT_REFERED_NAME</name>
                            <value/>
                        </genAttrElem>
                        <genAttrElem>
                            <name>STOP_POINT_REFERED_NAMEWITHPLACE</name>
                            <value/>
                        </genAttrElem>
                        <genAttrElem>
                            <name>STOP_AREA_NAME</name>
                            <value>Bus</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>STOP_GLOBAL_ID</name>
                            <value>de:5113:9159</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>STOPPOINT_GLOBAL_ID</name>
                            <value>de:5113:9159:3:1</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>IDENTIFIER</name>
                            <value>1</value>
                        </genAttrElem>
                    </genAttrList>
                </coordInfoItem>
                ''',
            'kwargs': {},
        })
        assert query.sourced().serialize() == {
            "@type": "platform.sourced",
            "source": "vrr",
            "time": "2016-07-02T12:49:39",
            "stop": {
                "@type": "stop.sourced",
                "source": "vrr",
                "time": "2016-07-02T12:49:39",
                "ifopt": "de:5113:9159",
                "city": {
                    "@type": "city.sourced",
                    "source": "vrr",
                    "time": "2016-07-02T12:49:39",
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
                "ids": {
                    "@type": "ids.frozen",
                    "vrr": "20009159"
                }
            },
            "area": {
                "@type": "stoparea.sourced",
                "source": "vrr",
                "time": "2016-07-02T12:49:39",
                "stop": {
                    "@type": "stop.sourced",
                    "source": "vrr",
                    "time": "2016-07-02T12:49:39",
                    "ifopt": "de:5113:9159",
                    "city": {
                        "@type": "city.sourced",
                        "source": "vrr",
                        "time": "2016-07-02T12:49:39",
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
                    "ids": {
                        "@type": "ids.frozen",
                        "vrr": "20009159"
                    }
                },
                "ifopt": "de:5113:9159:3",
                "name": "Bus",
                "ids": {
                    "@type": "ids.frozen",
                    "vrr": "20009159-3"
                }
            },
            "ifopt": "de:5113:9159:3:1",
            "platform_type": "street",
            "name": "1",
            "coords": [
                51.462965,
                6.954362
            ],
            "ids": {
                "@type": "ids.frozen",
                "vrr": "20009159-3-1"
            }
        }


class TestCoordInfoPOI:
    def test_base(self):
        query = Serializable.unserialize({
            '@type': 'poi.parser.efa.parsers.coordinfoCoordInfoPOI',
            'api': 'vrr',
            'time': '2016-07-02T12:57:42',
            'data': '''
                <coordInfoItem distance="748" gisID="3521" gisLayer="VRR" id="VRR-3521" locality="Essen" name="Matthäuskirche" omc="5113000" stateless="poiID:3521:5113000:-1:Matthäuskirche:Essen:Matthäuskirche:ANY:POI:773813:5295893:MRCV:VRR" type="POI_AREA">
                    <itdPathCoordinates>
                        <coordEllipsoid>WGS84</coordEllipsoid>
                        <coordType>GEO_DECIMAL</coordType>
                        <itdCoordinateBaseElemList>
                            <itdCoordinateBaseElem>
                                <x>6951280</x>
                                <y>51465808</y>
                            </itdCoordinateBaseElem>
                        </itdCoordinateBaseElemList>
                    </itdPathCoordinates>
                    <genAttrList>
                        <genAttrElem>
                            <name>POI_DRAW_CLASS_TYPE</name>
                            <value>AREA</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>POI_DRAW_CLASS</name>
                            <value>PoiReligion</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>POI_HIERARCHY_KEY</name>
                            <value>JC</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>POI_HIERARCHY_1</name>
                            <value>Anbetungsort</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>POI_HIERARCHY_KEY</name>
                            <value>J</value>
                        </genAttrElem>
                        <genAttrElem>
                            <name>POI_HIERARCHY_0</name>
                            <value>Sehnswürdigkeiten</value>
                        </genAttrElem>
                    </genAttrList>
                </coordInfoItem>
                ''',
            'kwargs': {},
        })
        assert query.sourced().serialize() == {
            "@type": "poi.sourced",
            "source": "vrr",
            "time": "2016-07-02T12:57:42",
            "poitype": "place_of_worship",
            "city": {
                "@type": "city.sourced",
                "source": "vrr",
                "time": "2016-07-02T12:57:42",
                "country": "de",
                "state": "nrw",
                "official_id": "05113000",
                "name": "Essen"
            },
            "name": "Matthäuskirche",
            "coords": [
                51.465808,
                6.95128
            ]
        }
