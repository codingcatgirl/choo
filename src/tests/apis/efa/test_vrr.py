import os

from choo.apis import *  # noqa
from choo.apis.requests import Request


class TestVrrPlatformQuery:
    def test_20160716_151208_613012(self):
        Request.requests_dump = [
            {
                "method": "POST",
                "url": "http://efa.vrr.de/standard/XML_STOPFINDER_REQUEST",
                "data": {
                    "SpEncId": 0,
                    "name_sf": "Essen Hbf",
                    "anyMaxSizeHitList": 1,
                    "language": "de",
                    "outputFormat": "XML",
                    "useHouseNumberList": "true",
                    "odvSugMacro": "true",
                    "type_sf": "any",
                    "locationServerActive": 1,
                    "coordOutputFormat": "WGS84"
                },
                "result": "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\r\n<itdRequest version=\"10.0.43.44\" language=\"de\" lengthUnit=\"METER\" sessionID=\"0\" client=\"python-requests/2.10.0\" clientIP=\"217.253.97.185\" serverID=\"EFA2.vrr.de_\" virtDir=\"standard\" now=\"2016-07-16T15:12:08\" nowWD=\"7\"><clientHeaderLines/><itdLayoutParams><itdLayoutParam name=\"sugImgPath\" value=\"/mdv/mdvStandardLayout2/images/sug/\"/><itdLayoutParam name=\"odvSugSort\" value=\"type:quality\"/></itdLayoutParams><itdStopFinderRequest requestID=\"0\"><itdOdv type=\"any\" usage=\"sf\" anyObjFilter=\"126\"><itdOdvPlace state=\"identified\" method=\"itp\"><odvPlaceElem omc=\"5113000\" placeID=\"18\" value=\"5113000:18\" span=\"0\" type=\"remote\" mainPlace=\"1\" stateless=\"placeID:5113000:18\">Essen</odvPlaceElem><odvPlaceInput></odvPlaceInput></itdOdvPlace><itdOdvName state=\"identified\" method=\"itp\"><itdMessage type=\"error\" module=\"BROKER\" code=\"-8010\"></itdMessage><odvNameElem x=\"7012941\" y=\"51451137\" mapName=\"WGS84\" id=\"20009289\" omc=\"5113000\" placeID=\"18\" anyType=\"stop\" locality=\"Essen\" objectName=\"Hauptbahnhof\" buildingName=\"\" buildingNumber=\"\" postCode=\"\" streetName=\"\" nameKey=\"\" mainLocality=\"Essen\" stateless=\"20009289\" gid=\"de:5113:9289\"><itdMapItemList><itdMapItem text=\"\" type=\"SM\"><itdImage src=\"vrr/09289_e_hbf_1.htm\" size=\"2\"/></itdMapItem></itdMapItemList>Essen, Hauptbahnhof</odvNameElem><odvNameInput>Essen Hbf</odvNameInput></itdOdvName><itdOdvAssignedStops select=\"0\"><itdOdvAssignedStop stopID=\"20009289\" x=\"7012941\" y=\"51451137\" mapName=\"WGS84\" value=\"20009289:Hauptbahnhof\" place=\"Essen\" nameWithPlace=\"Essen Hauptbahnhof\" distanceTime=\"0\" isTransferStop=\"0\" vm=\"100\" gid=\"de:5113:9289\">Hauptbahnhof</itdOdvAssignedStop></itdOdvAssignedStops></itdOdv><itdDateTime ttpFrom=\"20151213\" ttpTo=\"20161210\"><itdDate weekday=\"7\" year=\"2016\" month=\"7\" day=\"16\"/><itdTime hour=\"15\" minute=\"12\"/></itdDateTime></itdStopFinderRequest></itdRequest>\r\n"  # noqa
            },
            {
                "method": "POST",
                "url": "http://efa.vrr.de/standard/XML_COORD_REQUEST",
                "data": {
                    "radius_1": 400,
                    "inclFilter": "1",
                    "outputFormat": "XML",
                    "coord": "7.012941:51.451137:WGS84",
                    "type_1": "BUS_POINT",
                    "language": "de",
                    "coordOutputFormat": "WGS84"
                },
                "result": "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\r\n<itdRequest version=\"10.0.43.44\" language=\"de\" lengthUnit=\"METER\" sessionID=\"0\" client=\"python-requests/2.10.0\" clientIP=\"217.253.97.185\" serverID=\"EFA2.vrr.de_\" virtDir=\"standard\" now=\"2016-07-16T15:12:08\" nowWD=\"7\"><clientHeaderLines/><itdCoordInfoRequest requestID=\"0\"><itdCoordInfo><coordInfoRequest max=\"-1\" purpose=\"\" deadline=\"0\"><itdCoord x=\"7012941\" y=\"51451137\" mapName=\"WGS84\"/><coordInfoFilterItemList><coordInfoFilterItem type=\"BUS_POINT\" radius=\"400\" inclDrawClasses=\"\" exclLayers=\"\" name=\"\" ratingMethod=\"NULL\" inclPOIHierarchy=\"\" clustering=\"0\"/></coordInfoFilterItemList></coordInfoRequest><coordInfoItemList><coordInfoItem type=\"BUS_POINT\" id=\"20009289-2-2\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"42\" stateless=\"20009289-2-2\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013111</x><y>51451350</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:2:2</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>2</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-6-6\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"43\" stateless=\"20009289-6-6\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012797</x><y>51451361</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:6:6</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>6</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-7-7\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"50\" stateless=\"20009289-7-7\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012824</x><y>51450868</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:7:7</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>7</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-3-3\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"54\" stateless=\"20009289-3-3\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013165</x><y>51450868</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:3:3</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>3</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-8-8\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"78\" stateless=\"20009289-8-8\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012806</x><y>51450706</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:8:8</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>8</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-1-1\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"107\" stateless=\"20009289-1-1\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013076</x><y>51451731</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:1:1</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>1</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-9-9\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"111\" stateless=\"20009289-9-9\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012734</x><y>51450527</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:9:9</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>9</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-92-10\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"122\" stateless=\"20009289-92-10\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014037</x><y>51451171</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>10</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl710</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:92:10</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>10</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-92-7\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"122\" stateless=\"20009289-92-7\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014010</x><y>51451300</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl710</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:92:7</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>7</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-97-12\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"122\" stateless=\"20009289-97-12\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014037</x><y>51451115</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>12</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>G1112</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:97:12</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>12</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-91-6\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"125\" stateless=\"20009289-91-6\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014001</x><y>51451361</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>6</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl4-6</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:91:6</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>6</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-97-11\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"127\" stateless=\"20009289-97-11\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014064</x><y>51451014</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>G1112</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:97:11</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>11</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-91-4\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"132\" stateless=\"20009289-91-4\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013983</x><y>51451495</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>4</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl4-6</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:91:4</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>4</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-90-2\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"141\" stateless=\"20009289-90-2\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013974</x><y>51451596</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>2</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl1+2</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:90:2</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>2</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-92-8\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"142\" stateless=\"20009289-92-8\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7011665</x><y>51451081</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>8</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl710</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:92:8</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>8</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-4-4\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"143\" stateless=\"20009289-4-4\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013686</x><y>51450482</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:4:4</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>4</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-90-1\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"154\" stateless=\"20009289-90-1\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7013956</x><y>51451719</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>1</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl1+2</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:90:1</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>1</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-13-3\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"162\" stateless=\"20009289-13-3\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012707</x><y>51450241</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>1+3</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:13:3</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>3</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-98-98g\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"162\" stateless=\"20009289-98-98g\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014369</x><y>51451305</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>G2122</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:98:98g</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>98g</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-13-1\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"167\" stateless=\"20009289-13-1\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012896</x><y>51450202</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>1+3</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:13:1</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>1</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-98-98\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"184\" stateless=\"20009289-98-98\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014594</x><y>51451176</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>G2122</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:98:98</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>98</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-5-5\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"206\" stateless=\"20009289-5-5\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014441</x><y>51450465</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:5:5</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>5</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-90-90\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"209\" stateless=\"20009289-90-90\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7014369</x><y>51451893</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>9</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl1+2</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:90:90</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>90</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-14-2\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"251\" stateless=\"20009289-14-2\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012159</x><y>51449822</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>2+4</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:14:2</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>2</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-14-4\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"255\" stateless=\"20009289-14-4\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7012303</x><y>51449766</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Bay</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>2+4</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:14:4</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>4</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-92-9\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"353\" stateless=\"20009289-92-9\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7016085</x><y>51451389</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>9</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>Gl710</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:92:9</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>9</value></genAttrElem></genAttrList></coordInfoItem><coordInfoItem type=\"BUS_POINT\" id=\"20009289-98-21\" name=\"Hauptbahnhof\" omc=\"5113000\" placeID=\"18\" locality=\"Essen\" gisLayer=\"SYS-STOPPOINT\" distance=\"430\" stateless=\"20009289-98-21\"><itdPathCoordinates><coordEllipsoid>WGS84</coordEllipsoid><coordType>GEO_DECIMAL</coordType><itdCoordinateBaseElemList><itdCoordinateBaseElem><x>7016534</x><y>51452027</y></itdCoordinateBaseElem></itdCoordinateBaseElemList></itdPathCoordinates><genAttrList><genAttrElem><name>STOP_POINT_LONGNAME</name><value>21</value></genAttrElem><genAttrElem><name>STOP_POINT_CHARACTERISTICS</name><value>Platform</value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAME</name><value></value></genAttrElem><genAttrElem><name>STOP_POINT_REFERED_NAMEWITHPLACE</name><value></value></genAttrElem><genAttrElem><name>STOP_AREA_NAME</name><value>G2122</value></genAttrElem><genAttrElem><name>STOP_GLOBAL_ID</name><value>de:5113:9289</value></genAttrElem><genAttrElem><name>STOPPOINT_GLOBAL_ID</name><value>de:5113:9289:98:21</value></genAttrElem><genAttrElem><name>IDENTIFIER</name><value>21</value></genAttrElem></genAttrList></coordInfoItem></coordInfoItemList></itdCoordInfo></itdCoordInfoRequest></itdRequest>\r\n"  # noqa
            }
        ]
        os.environ["CHOO_REQUESTS_TEST"] = "1"
        os.environ["CHOO_REQUESTS_TEST_ORDERED"] = "1"
        query = vrr.platforms.where(stop__name='Essen Hbf')
        assert query.execute().serialize() == {
            "@type": "platform.query",
            "api": "vrr",
            "obj": {
                "@type": "platform",
                "stop": {
                    "@type": "stop",
                    "name": "Essen Hbf"
                }
            },
            "settings": {
                "limit": None,
                "max_distance": 1000
            },
            "results": [
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:2",
                            "vrr": "20009289-2"
                        }
                    },
                    "platform_type": "street",
                    "name": "2",
                    "coords": [
                        51.45135,
                        7.013111
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:2:2",
                        "vrr": "20009289-2-2"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:6",
                            "vrr": "20009289-6"
                        }
                    },
                    "platform_type": "street",
                    "name": "6",
                    "coords": [
                        51.451361,
                        7.012797
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:6:6",
                        "vrr": "20009289-6-6"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:7",
                            "vrr": "20009289-7"
                        }
                    },
                    "platform_type": "street",
                    "name": "7",
                    "coords": [
                        51.450868,
                        7.012824
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:7:7",
                        "vrr": "20009289-7-7"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:3",
                            "vrr": "20009289-3"
                        }
                    },
                    "platform_type": "street",
                    "name": "3",
                    "coords": [
                        51.450868,
                        7.013165
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:3:3",
                        "vrr": "20009289-3-3"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:8",
                            "vrr": "20009289-8"
                        }
                    },
                    "platform_type": "street",
                    "name": "8",
                    "coords": [
                        51.450706,
                        7.012806
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:8:8",
                        "vrr": "20009289-8-8"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:1",
                            "vrr": "20009289-1"
                        }
                    },
                    "platform_type": "street",
                    "name": "1",
                    "coords": [
                        51.451731,
                        7.013076
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:1:1",
                        "vrr": "20009289-1-1"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:9",
                            "vrr": "20009289-9"
                        }
                    },
                    "platform_type": "street",
                    "name": "9",
                    "coords": [
                        51.450527,
                        7.012734
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:9:9",
                        "vrr": "20009289-9-9"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl710",
                        "ids": {
                            "ifopt": "de:5113:9289:92",
                            "vrr": "20009289-92"
                        }
                    },
                    "platform_type": "platform",
                    "name": "10",
                    "coords": [
                        51.451171,
                        7.014037
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:92:10",
                        "vrr": "20009289-92-10"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl710",
                        "ids": {
                            "ifopt": "de:5113:9289:92",
                            "vrr": "20009289-92"
                        }
                    },
                    "platform_type": "street",
                    "name": "7",
                    "coords": [
                        51.4513,
                        7.01401
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:92:7",
                        "vrr": "20009289-92-7"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "G1112",
                        "ids": {
                            "ifopt": "de:5113:9289:97",
                            "vrr": "20009289-97"
                        }
                    },
                    "platform_type": "platform",
                    "name": "12",
                    "coords": [
                        51.451115,
                        7.014037
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:97:12",
                        "vrr": "20009289-97-12"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl4-6",
                        "ids": {
                            "ifopt": "de:5113:9289:91",
                            "vrr": "20009289-91"
                        }
                    },
                    "platform_type": "platform",
                    "name": "6",
                    "coords": [
                        51.451361,
                        7.014001
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:91:6",
                        "vrr": "20009289-91-6"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "G1112",
                        "ids": {
                            "ifopt": "de:5113:9289:97",
                            "vrr": "20009289-97"
                        }
                    },
                    "platform_type": "street",
                    "name": "11",
                    "coords": [
                        51.451014,
                        7.014064
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:97:11",
                        "vrr": "20009289-97-11"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl4-6",
                        "ids": {
                            "ifopt": "de:5113:9289:91",
                            "vrr": "20009289-91"
                        }
                    },
                    "platform_type": "platform",
                    "name": "4",
                    "coords": [
                        51.451495,
                        7.013983
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:91:4",
                        "vrr": "20009289-91-4"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl1+2",
                        "ids": {
                            "ifopt": "de:5113:9289:90",
                            "vrr": "20009289-90"
                        }
                    },
                    "platform_type": "platform",
                    "name": "2",
                    "coords": [
                        51.451596,
                        7.013974
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:90:2",
                        "vrr": "20009289-90-2"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl710",
                        "ids": {
                            "ifopt": "de:5113:9289:92",
                            "vrr": "20009289-92"
                        }
                    },
                    "platform_type": "platform",
                    "name": "8",
                    "coords": [
                        51.451081,
                        7.011665
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:92:8",
                        "vrr": "20009289-92-8"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:4",
                            "vrr": "20009289-4"
                        }
                    },
                    "platform_type": "street",
                    "name": "4",
                    "coords": [
                        51.450482,
                        7.013686
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:4:4",
                        "vrr": "20009289-4-4"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl1+2",
                        "ids": {
                            "ifopt": "de:5113:9289:90",
                            "vrr": "20009289-90"
                        }
                    },
                    "platform_type": "platform",
                    "name": "1",
                    "coords": [
                        51.451719,
                        7.013956
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:90:1",
                        "vrr": "20009289-90-1"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "1+3",
                        "ids": {
                            "ifopt": "de:5113:9289:13",
                            "vrr": "20009289-13"
                        }
                    },
                    "platform_type": "street",
                    "name": "3",
                    "coords": [
                        51.450241,
                        7.012707
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:13:3",
                        "vrr": "20009289-13-3"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "G2122",
                        "ids": {
                            "ifopt": "de:5113:9289:98",
                            "vrr": "20009289-98"
                        }
                    },
                    "platform_type": "unknown",
                    "name": "98g",
                    "coords": [
                        51.451305,
                        7.014369
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:98:98g",
                        "vrr": "20009289-98-98g"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "1+3",
                        "ids": {
                            "ifopt": "de:5113:9289:13",
                            "vrr": "20009289-13"
                        }
                    },
                    "platform_type": "street",
                    "name": "1",
                    "coords": [
                        51.450202,
                        7.012896
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:13:1",
                        "vrr": "20009289-13-1"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "G2122",
                        "ids": {
                            "ifopt": "de:5113:9289:98",
                            "vrr": "20009289-98"
                        }
                    },
                    "platform_type": "unknown",
                    "name": "98",
                    "coords": [
                        51.451176,
                        7.014594
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:98:98",
                        "vrr": "20009289-98-98"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "ids": {
                            "ifopt": "de:5113:9289:5",
                            "vrr": "20009289-5"
                        }
                    },
                    "platform_type": "street",
                    "name": "5",
                    "coords": [
                        51.450465,
                        7.014441
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:5:5",
                        "vrr": "20009289-5-5"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl1+2",
                        "ids": {
                            "ifopt": "de:5113:9289:90",
                            "vrr": "20009289-90"
                        }
                    },
                    "platform_type": "platform",
                    "name": "9",
                    "coords": [
                        51.451893,
                        7.014369
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:90:90",
                        "vrr": "20009289-90-90"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "2+4",
                        "ids": {
                            "ifopt": "de:5113:9289:14",
                            "vrr": "20009289-14"
                        }
                    },
                    "platform_type": "street",
                    "name": "2",
                    "coords": [
                        51.449822,
                        7.012159
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:14:2",
                        "vrr": "20009289-14-2"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "2+4",
                        "ids": {
                            "ifopt": "de:5113:9289:14",
                            "vrr": "20009289-14"
                        }
                    },
                    "platform_type": "street",
                    "name": "4",
                    "coords": [
                        51.449766,
                        7.012303
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:14:4",
                        "vrr": "20009289-14-4"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "Gl710",
                        "ids": {
                            "ifopt": "de:5113:9289:92",
                            "vrr": "20009289-92"
                        }
                    },
                    "platform_type": "platform",
                    "name": "9",
                    "coords": [
                        51.451389,
                        7.016085
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:92:9",
                        "vrr": "20009289-92-9"
                    }
                },
                {
                    "@type": "platform.sourced",
                    "source": "vrr",
                    "stop": {
                        "@type": "stop.sourced",
                        "source": "vrr",
                        "city": {
                            "@type": "city.sourced",
                            "source": "vrr",
                            "country": "de",
                            "state": "nrw",
                            "name": "Essen",
                            "ids": {
                                "vrr": "placeID:5113000:18",
                                "de": "05113000"
                            }
                        },
                        "name": "Hauptbahnhof",
                        "coords": [
                            51.451137,
                            7.012941
                        ],
                        "ids": {
                            "ifopt": "de:5113:9289",
                            "vrr": "20009289"
                        }
                    },
                    "area": {
                        "@type": "stoparea.sourced",
                        "source": "vrr",
                        "stop": {
                            "@type": "stop.sourced",
                            "source": "vrr",
                            "city": {
                                "@type": "city.sourced",
                                "source": "vrr",
                                "country": "de",
                                "state": "nrw",
                                "name": "Essen",
                                "ids": {
                                    "vrr": "placeID:5113000:18",
                                    "de": "05113000"
                                }
                            },
                            "name": "Hauptbahnhof",
                            "coords": [
                                51.451137,
                                7.012941
                            ],
                            "ids": {
                                "ifopt": "de:5113:9289",
                                "vrr": "20009289"
                            }
                        },
                        "name": "G2122",
                        "ids": {
                            "ifopt": "de:5113:9289:98",
                            "vrr": "20009289-98"
                        }
                    },
                    "platform_type": "platform",
                    "name": "21",
                    "coords": [
                        51.452027,
                        7.016534
                    ],
                    "ids": {
                        "ifopt": "de:5113:9289:98:21",
                        "vrr": "20009289-98-21"
                    }
                }
            ]
        }
        os.environ.pop("CHOO_REQUESTS_TEST")
        os.environ.pop("CHOO_REQUESTS_TEST_ORDERED")
