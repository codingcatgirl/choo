#!/usr/bin/env python3
from models import SearchResults
from models import Location, Stop, POI, Address
from models import TimeAndPlace, RealtimeTime
from models import Ride, Line, LineType
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from .base import API
import requests
import re


class EFA(API):
    name = 'efa'
    base_url = None
    country = None

    def get_stop(self, stop: Stop):
        assert isinstance(stop, Stop)

    def get_stop_rides(self, stop: Stop, time: datetime=None):
        if time is None:
            time = datetime.now()
        stop = self._convert_location(stop)

        post = {
            'command': '',
            'coordOutputFormat': 'WGS84',
            'itdDateDay': time.day,
            'itdDateMonth': time.month,
            'itdDateYear': time.year,
            'itdTimeHour': time.hour,
            'itdTimeMinute': time.minute,
            'language': 'de',
            'lsShowTrainsExplicit': 1,
            'mode': 'direct',
            'outputFormat': 'XML',
            'itOptionsActive': 1,
            'ptOptionsActive': 1,
            # 'includeCompleteStopSeq': 1,
            'useRealtime': 1,
            'requestID': 0,
            'sessionID': 0
        }
        post.update({'%s_dm' % name: value for name, value in stop.items()})

        xml = self._post('XSLT_DM_REQUEST', post)
        result = self._parse_stop_finder_request(xml)

        return result

    def _convert_location(self, location: Location):
        myid, raw = self._my_data(location)
        if isinstance(location, Stop):
            if myid is not None:
                return {'type': 'stop', 'place': None, 'name': str(myid)}
            else:
                return {'type': 'stop', 'place': location.city, 'name': location.name}
        else:
            raise NotImplementedError

    def _post(self, endpoint, data):
        text = requests.post(self.base_url+endpoint, data=data).text
        open('dump.xml', 'w').write(text)
        return ET.fromstring(text)

    def _parse_stop_finder_request(self, xml):
        data = xml.find('./itdDepartureMonitorRequest')

        stop = self._parse_odv(data.find('./itdOdv'))

        if type(stop) == list:
            return SearchResults(stop, api=self)

        #lineslist = data.find('./itdServingLines')
        #if lineslist is not None:
        #	result.lines = []
        #	lines = lineslist.findall('./itdServingLine')
        #	for line in lines:
        #		result.lines.append(self.MOT(line))

        departureslist = data.find('./itdDepartureList')
        stop.rides = self._parse_departures(departureslist)

        return stop
        #return result

    def _parse_odv(self, data):
        odvtype = data.attrib['type']
        results = []

        # Place
        p = data.find('./itdOdvPlace')
        if p.attrib['state'] == 'empty':
            city = None
        elif p.attrib['state'] != 'identified':
            if p.attrib['state'] == 'list':
                pe = p.findall('./odvPlaceElem')
                for item in pe:
                    location = Location(self.country, city=item.text)
                    location.raws[self.name] = pe
                    results.append(location)
            return results
        else:
            pe = p.find('./odvPlaceElem')
            city = pe.text

        # Location
        n = data.find('./itdOdvName')
        if n.attrib['state'] == 'empty':
            if city is not None:
                location = Location(self.country, city)
                location.raws[self.name] = pe
                results.append(location)
            return results
        elif n.attrib['state'] != 'identified':
            if n.attrib['state'] == 'list':
                ne = n.findall('./odvNameElem')
                results = [self._name_elem(item, city, odvtype) for item in ne]
                results.sort(key=lambda odv: odv[1], reverse=True)
            return results
        else:
            ne = n.find('./odvNameElem')
            return self._name_elem(ne, city, odvtype)[0]

    def _name_elem(self, data, city, odvtype):
        if 'anyType' in data.attrib and data.attrib['anyType'] != '':
            odvtype = data.attrib['anyType']

        mycity = city
        if mycity is None and 'locality' in data.attrib and data.attrib['locality'] != '':
            mycity = data.attrib['locality']

        location = None
        name = data.attrib['objectName'] if 'objectName' in data.attrib else data.text
        if odvtype == 'stop':
            location = Stop(self.country, mycity, name)
        elif odvtype == 'poi':
            location = POI(self.country, mycity, name)
        elif odvtype == 'street':
            location = Address(self.country, mycity, name)
        elif odvtype in ('singlehouse', 'coord', 'address'):
            location = Address(self.country, mycity, name)
            location.street = data.attrib['streetName'] if 'streetName' in data.attrib else None
            location.number = data.attrib['buildingNumber'] if 'buildingNumber' in data.attrib else None
            location.number = data.attrib['houseNumber'] if 'houseNumber' in data.attrib else None
            location.name = '%s %s' % (location.street, location.number)
        else:
            raise NotImplementedError('Unknown odvtype: %s' % odvtype)

        if 'stopID' in data.attrib and data.attrib['stopID'] != '':
            if location is None:
                location = Stop(self.country, mycity, name)
            location.ids[self.name] = int(data.attrib['stopID'])
        elif 'id' in data.attrib and data.attrib['id'] != '':
            if location is None:
                location = POI(self.country, mycity, name)
            location.ids[self.name] = int(data.attrib['id'])
        elif location is None:
            location = Address(self.country, mycity, name)

        score = int(data.attrib['matchQuality']) if 'matchQuality' in data.attrib else 0

        if 'x' in data.attrib:
            location.coords = (float(data.attrib['x']) / 1000000, float(data.attrib['y']) / 1000000)

        return location, score

    def _parse_departures(self, data, stop=None):
        results = []
        departures = data.findall('./itdDeparture')
        for departure in departures:
            # result.departures.append((self.MOT(departure.find('./itdServingLine')), self.TripPoint(departure)))
            origin, line, destination = self._parse_mot(departure.find('./itdServingLine'))
            ride = Ride(line)
            if origin is not None:
                ride.append(TimeAndPlace(origin))
            ride.append(None)
            pointer = ride.append(self._parse_trip_point(departure))
            ride.append(None)
            if destination is not None:
                ride.append(TimeAndPlace(destination))
            results.append(ride[pointer:])
        return results

    def _parse_datetime(self, data):
        d = data.find('./itdDate').attrib
        t = data.find('./itdTime').attrib
        if d['weekday'] == '-1' or d['day'] == '-1' or t['minute'] == '-1':
            return None
        result = datetime(int(d['year']), int(d['month']), int(d['day']), min(int(t['hour']), 23), int(t['minute']))
        if int(t['hour']) == 24:
            result += timedelta(1)
        return result

    def _parse_mot(self, data):
        result = Line()
        if 'motType' not in data.attrib:
            return None

        if 'name' in data.attrib:
            result.name = data.attrib['name']
        elif 'number' in data.attrib:
            result.name = data.attrib['number']
            train = data.find('./itdNoTrain')
            if train is not None and 'name' in train.attrib and train.attrib['name'] not in result.name:
                result.name = '%s %s' % (train.attrib['name'], result.name)

        if 'shortname' in data.attrib:
            result.shortname = data.attrib['shortname']
            if 'trainType' in data.attrib and data.attrib['trainType'] not in result.shortname:
                result.shortname = '%s%s' % (data.attrib['trainType'], result.shortname)
            elif result.shortname == '':
                train = data.find('./itdNoTrain')
                if train is not None and 'type' in train.attrib and train.attrib['type'] not in result.shortname:
                    result.shortname = train.attrib['type']
        elif 'symbol' in data.attrib:
            result.shortname = data.attrib['symbol']

        if 'productName' in data.attrib:
            result.product = data.attrib['productName']
        else:
            notrain = data.find('./itdNoTrain')
            if notrain is not None and 'name' in notrain.attrib:
                result.product = notrain.attrib['name']
            else:
                train = data.find('./itdTrain')
                if train is not None and 'name' in train.attrib:
                    result.product = train.attrib['name']

        destination = Stop(self.country, None, data.attrib['direction' if 'direction' in data.attrib else 'destination'])
        if data.attrib['destID'] != '':
            destination.ids[self.name] = int(data.attrib['destID'])

        origin = Stop(self.country, None, data.attrib['directionFrom']) if 'directionFrom' in data.attrib and data.attrib['directionFrom'] else None

        routedescription = data.find('./itdRouteDescText')
        if routedescription is not None:
            result.route = routedescription.text

        diva = data.find('./motDivaParams')
        if diva is not None:
            result.network = diva.attrib['network']
            result.line = diva.attrib['line']
            result.direction  = diva.attrib['direction']

        mottype = int(data.attrib['motType'])
        result.linetype = LineType(('localtrain', 'urban', 'metro', 'urban', 'tram',
                                    'citybus', 'regionalbus', 'expressbus', 'suspended',
                                    'ship', 'dialable', 'others')[mottype])

        if mottype == 0:
            if result.network == 'ddb':
                if result.line[0:2] in ('96', '91'):
                    result.linetype.name = 'longdistance'
                elif result.line[0:2] == '98':
                    result.linetype.name = 'highspeed'

        op = data.find('./itdOperator')
        if op is not None:
            result.operator = op.find('./name').text
        return origin, result, destination

    def _parse_trip_point(self, data, walk=False):
        # Todo: POI
        city = data.attrib['locality'] if 'locality' in data.attrib and data.attrib['locality'] != '' else None
        name = data.attrib['nameWO'] if 'nameWO' in data.attrib and data.attrib['nameWO'] != '' else data.attrib['name']

        if walk and data.attrib['area'] == '0':
            location = Address(self.country, city, name)
        else:
            location = Stop(self.country, city, name)
            location.ids[self.name] = int(data.attrib['stopID'])

        result = TimeAndPlace(location)

        if 'x' in data.attrib:
            result.coords = (float(data.attrib['x']) / 1000000, float(data.attrib['y']) / 1000000)

        result.platform = data.attrib['platform']
        if result.platform.strip() == '':
            match = re.search(r'[0-9].*$', data.attrib['platformName'])
            if match is not None:
                result.platform = match.group(0)

        if 'usage' in data.attrib and data.attrib['usage'] != '':
            times = []
            if data.find('./itdDateTimeTarget'):
                times.append(self._parse_datetime(data.find('./itdDateTimeTarget')))
            if data.find('./itdDateTime'):
                times.append(self._parse_datetime(data.find('./itdDateTime')))

            thetime = None
            livetime = None
            if len(times) > 0:
                thetime = times[0]
            if len(times) == 2 and not walk:
                livetime = times[1]

            if data.attrib['usage'] == 'departure':
                result.departure = RealtimeTime(time=thetime, livetime=livetime)
            elif data.attrib['usage'] == 'arival':
                result.arrival = RealtimeTime(time=thetime, livetime=livetime)

        elif 'countdown' in data.attrib:
            times = []
            if data.find('./itdDateTime'):
                times.append(self._parse_datetime(data.find('./itdDateTime')))
            if data.find('./itdRTDateTime'):
                times.append(self._parse_datetime(data.find('./itdRTDateTime')))

            thetime = None
            livetime = None
            if len(times) > 0:
                thetime = times[0]
            if len(times) == 2 and not walk:
                livetime = times[1]
            result.departure = RealtimeTime(time=thetime, livetime=livetime)

        else:
            times = []
            for itddatetime in data.findall('./itdDateTime'):
                times.append(self._parse_datetime(itddatetime))

            if len(times) > 0 and times[0] is not None:
                delay = None
                if 'arrDelay' in data.attrib and data.attrib['arrDelay'] != '-1':
                    delay = timedelta(minutes=int(data.attrib['arrDelay']))
                result.arrival = RealtimeTime(time=times[0], delay=delay)

            if len(times) > 1 and times[1] is not None:
                delay = None
                if 'depDelay' in data.attrib and data.attrib['depDelay'] != '-1':
                    delay = timedelta(minutes=int(data.attrib['depDelay']))
                result.departure = RealtimeTime(time=times[1], delay=delay)

        #for genattr in data.findall('./genAttrList/genAttrElem'):
        #	name = genattr.find('name').text
        #	value = genattr.find('value').text
        #	if name == 'platformChange' and value == 'changed':
        #		result.changed_platform = True

        return result
