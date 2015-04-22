#!/usr/bin/env python3
from models import SearchResults
from models import Location, Stop, POI, Address
from models import TimeAndPlace, RealtimeTime
from models import Ride, Line, LineType, LineTypes
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from .base import API
import requests
import re


class EFA(API):
    name = 'efa'
    base_url = None
    country = None

    def get_stop(self, stop: Stop, must_get_departures=False):
        assert isinstance(stop, Stop)
        return self.get_stop_rides(stop)

    def get_stop_rides(self, stop: Stop):
        return self._departure_monitor_request(stop)
        
    def search_trips(self, trip: Stop):
        now = datetime.datetime.now()
        
        assert trip.walk_speed in ('slow', 'normal', 'fast')
        
        linetypes = trip.linetypes
        if linetypes is None:
            linetypes = LineTypes()
        assert isinstance(linetypes, LineTypes)
        
        departure = trip.departure
        arrival = trip.arrival
        assert departure is None or isinstance(departure, RealtimeTime) or isinstance(departure, datetime)
        assert arrival is None or isinstance(arrival, RealtimeTime) or isinstance(arrival, datetime)
        
        if isinstance(departure, datetime):
            departure = RealtimeTime(departure)
        if isinstance(arrival, datetime):
            arrival = RealtimeTime(arrival)
            
        if departure is not None:
            deparr = 'dep'
            time_ = departure.livetime
        elif arrival is not None:
            deparr = 'arr'
            time_ = arrival.livetime
        else:
            deparr = 'dep'
            time_ = now
                
        changes = trip.changes
        if changes is None:
            changes = 9
        
        post = {
			'changeSpeed': trip.walk_speed,
			'command': '',
			'imparedOptionsActive': 1,
			
			'includedMeans': 'checkbox',
			'itOptionsActive': 1,
			'itdDateDay': time_.day,
			'itdDateMonth': time_.month,
			'itdDateYear': time_.year,
			'itdTimeHour': time_.hour,
			'itdTimeMinute': time_.minute,
			'itdTripDateTimeDepArr': deparr,
			'language': 'de',
			'locationServerActive': 1,
			'maxChanges': changes if type(changes) == int else max(changes),
			'name_via': '',#.decode('utf-8').encode('iso-8859-1'),
			'nextDepsPerLeg': 1,
			'place_via': '',#decode('utf-8').encode('iso-8859-1'),
			'ptOptionsActive': 1,
			'requestID': 0,
			'routeType': {'speed':'LEASTTIME', 'waittime':'LEASTINTERCHANGE', 'distance':'LEASTWALKING'}[select_interchange_by],
			'sessionID': 0,
			'text': 1993,
			'type_via': 'stop'
		}
        
        if ('localtrain', 'longdistance', 'highspeed') in linetypes:
            post['inclMOT_0'] = 'on'
            
        if 'highspeed' in linetypes:
            post['lineRestriction'] = 400
        elif 'longdistance' in linetypes:
            post['lineRestriction'] = 401
        else:
            post['lineRestriction'] = 403
            
        if 'urban' in linetypes:
            post['inclMOT_1'] = 'on'
            
        if 'metro' in linetypes:
            post['inclMOT_2'] = 'on'
            post['inclMOT_3'] = 'on'
            
        if 'tram' in linetypes:
            post['inclMOT_4'] = 'on'
            
        if 'citybus' in linetypes:
            post['inclMOT_5'] = 'on'
            
        if 'regionalbus' in linetypes:
            post['inclMOT_6'] = 'on'
            
        if 'expressbus' in linetypes:
            post['inclMOT_7'] = 'on'
            
        if 'suspended' in linetypes:
            post['inclMOT_8'] = 'on'
            
        if 'ship' in linetypes:
            post['inclMOT_9'] = 'on'
            
        if 'dialable' in linetypes:
            post['inclMOT_10'] = 'on'
            
        if 'other' in linetypes:
            post['inclMOT_11'] = 'on'
            
        assert isinstance(trip.origin, Location)
        assert isinstance(trip.destination, Location)
        
        post.update(self._convert_location(self, trip.origin, '%s_origin'))
        post.update(self._convert_location(self, trip.destination, '%s_destination'))
        #todo: via
        
        print(post)
        
    def get_trip(self, trip: Stop):
        pass
        

    # Internal methods start here

    def _post(self, endpoint, data):
        text = requests.post(self.base_url+endpoint, data=data).text
        # open('dump.xml', 'w').write(text)
        return ET.fromstring(text)

    def _convert_location(self, location: Location, wrap=''):
        """ Convert a Location into POST parameters for the EFA Requests """
        myid, raw = self._my_data(location)

        city = location.city

        if location.name is None:
            if location.coords is not None:
                r = {'type': 'coord', 'name': '%.6f:%.6f:WGS84' % (reversed(location.coords))}
            else:
                r = {'type': 'stop', 'place': city, 'name': ''}
        elif isinstance(location, Stop):
            if myid is not None:
                r = {'type': 'stop', 'place': None, 'name': str(myid)}
            else:
                r = {'type': 'stop', 'place': city, 'name': location.name}
        elif isinstance(location, Address):
            r = {'type': 'address', 'place': city, 'name': location.name}
        elif isinstance(location, POI):
            if myid is not None:
                r = {'type': 'poiID', 'name': str(myid)}
            else:
                r = {'type': 'poi', 'place': city, 'name': location.name}
        elif isinstance(location, Location):
            r = {'type': 'any', 'place': city, 'name': location.name if location.name else None}
        else:
            raise NotImplementedError

        if r['place'] is None:
            del r['place']
            
        if suffix:
            r = {wrap % n: v for n, v in r.items()}

        return r

    def _stop_finder_request(self, stop: Stop):
        """ Searches a Stop; Returns a SearchResult(Stop) """
        mystop = self._convert_location(stop)

        post = {
            'language': 'de',
            'outputFormat': 'XML',
            'odvSugMacro': 'true'
        }
        post.update({'%s_sf' % name: value for name, value in mystop.items()})

        xml = self._post('XSLT_STOPFINDER_REQUEST', post)
        data = xml.find('./itdStopFinderRequest')

        results = self._parse_odv(data.find('./itdOdv'))
        if type(results) != list:
            results = [results]
        results = [result for result in results if isinstance(stop, result[0].__class__)]

        return SearchResults(results, api=self.name)

    def _departure_monitor_request(self, stop: Stop, time: datetime=None):
        """ Fills in Stop.rides; Can Return A SearchResult(Stop) without rides. """
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
        data = xml.find('./itdDepartureMonitorRequest')

        stop = self._parse_odv(data.find('./itdOdv'))

        if type(stop) == list:
            return SearchResults(stop, api=self.name)

        lineslist = data.find('./itdServingLines')
        if lineslist is not None:
            stop.lines = []
            lines = lineslist.findall('./itdServingLine')
            for line in lines:
                origin, destination, line, rideid, ridenum = self._parse_mot(line)
                line.first_stop = origin
                line.last_stop = destination
                stop.lines.append(line)

        departureslist = data.find('./itdDepartureList')
        stop.rides = self._parse_departures(departureslist, stop)

        return stop

    def _parse_odv(self, data):
        """ Parse an ODV (OriginDestinationVia) XML node """
        odvtype = data.attrib['type']
        results = []

        # Place.city
        p = data.find('./itdOdvPlace')
        if p.attrib['state'] == 'empty':
            city = None
        elif p.attrib['state'] != 'identified':
            if p.attrib['state'] == 'list':
                pe = p.findall('./odvPlaceElem')
                for item in pe:
                    location = Location(self.country, city=item.text)
                    location._raws[self.name] = ET.tostring(pe, 'utf-8').decode()
                    results.append(location)
            return results
        else:
            pe = p.find('./odvPlaceElem')
            city = pe.text

        # Location.name
        n = data.find('./itdOdvName')
        if n.attrib['state'] == 'empty':
            if city is not None:
                location = Location(self.country, city)
                location._raws[self.name] = ET.tostring(pe, 'utf-8').decode()
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
            result = self._name_elem(ne, city, odvtype)[0]
            result._raws[self.name] = ET.tostring(data, 'utf-8').decode()
            return result

    def _name_elem(self, data, city, odvtype):
        """ Parses the odvNameElem of an ODV """
        # AnyTypes are used in some EFA instances instead of ODV types
        anytype = data.attrib.get('anyType', '')
        odvtype = anytype if anytype else odvtype

        # Even though we got the city, some APIs deliver it only in the odvNameElem…
        locality = data.attrib.get('locality', '')
        city = locality if locality else city

        # What kind of location is it? Fill in attributes.
        location = None
        name = data.attrib.get('objectName', data.text)
        if odvtype == 'stop':
            location = Stop(self.country, city, name)
        elif odvtype == 'poi':
            location = POI(self.country, city, name)
        elif odvtype == 'street':
            location = Address(self.country, city, name)
        elif odvtype in ('singlehouse', 'coord', 'address'):
            location = Address(self.country, city, name)
            location.street = data.attrib['streetName'] if 'streetName' in data.attrib else None
            location.number = data.attrib['buildingNumber'] if 'buildingNumber' in data.attrib else None
            location.number = data.attrib['houseNumber'] if 'houseNumber' in data.attrib else None
            location.name = '%s %s' % (location.street, location.number)
        else:
            raise NotImplementedError('Unknown odvtype: %s' % odvtype)

        # IDs can come in different ways… Sometimes this is the only way to determine the Location type…
        stopid = data.attrib.get('stopID', '')
        myid = data.attrib.get('id', '')
        if stopid:
            if location is None:
                location = Stop(self.country, city, name)
            if isinstance(location, Stop):
                location._ids[self.name] = int(stopid)
        elif myid:
            if location is None:
                location = POI(self.country, city, name)
            location._ids[self.name] = int(myid)
        elif location is None:
            # Still no clue about the Type? Well, it's an Address then.
            location = Address(self.country, city, name)

        # This is used when we got more than one Location
        score = int(data.attrib.get('matchQuality', 0))

        # Coordinates
        if 'x' in data.attrib:
            location.coords = (float(data.attrib['y']) / 1000000, float(data.attrib['x']) / 1000000)

        return location, score

    def _parse_departures(self, data, stop=None):
        """ Parses itdDeparture into a List of RideSegment """
        results = []
        departures = data.findall('./itdDeparture')
        for departure in departures:
            # Get Line Information
            origin, destination, line, rideid, ridenum = self._parse_mot(departure.find('./itdServingLine'))

            # Build Ride Objekt with known stops
            ride = Ride(line, ridenum)
            ride._ids[self.name] = rideid
            if origin is not None:
                ride.append(TimeAndPlace(origin))
            ride.append(None)
            mypoint = self._parse_trip_point(departure)
            mypoint.stop = stop
            pointer = ride.append(mypoint)
            ride.append(None)
            if destination is not None:
                ride.append(TimeAndPlace(destination))

            # Return RideSegment from the Station we depart from on
            results.append(ride[pointer:])
        return results

    def _parse_datetime(self, data):
        """ Create a datetime from itdDate and itdTime """
        d = data.find('./itdDate').attrib
        t = data.find('./itdTime').attrib

        # -! means nope, there is no time known
        if d['weekday'] == '-1' or d['day'] == '-1' or t['minute'] == '-1':
            return None

        # convert time – the EFA API likes to talk abou 24:00, so we have to correct that.
        result = datetime(int(d['year']), int(d['month']), int(d['day']), min(int(t['hour']), 23), int(t['minute']))
        if int(t['hour']) == 24:
            result += timedelta(1)
        return result

    def _parse_mot(self, data):
        """ Parse a itdServingLine Node into something nicer """
        line = Line()

        # no motType – that means we are walking or something similar
        if 'motType' not in data.attrib:
            return None

        # determine Type
        mottype = int(data.attrib['motType'])
        line.linetype = LineType(('localtrain', 'urban', 'metro', 'urban', 'tram',
                                  'citybus', 'regionalbus', 'expressbus', 'suspended',
                                  'ship', 'dialable', 'others')[mottype])

        # general Line and Ride attributes
        line._raws[self.name] = ET.tostring(data, 'utf-8').decode()
        rideid = data.attrib['stateless']
        diva = data.find('./motDivaParams')
        if diva is not None:
            line.network = diva.attrib['network']
            ridenum = diva.attrib['line']

        op = data.find('./itdOperator')
        if op is not None:
            line.operator = op.find('./name').text

        # We behave different for trains and non-trains
        if mottype == 0:
            line.name = data.attrib['symbol']
            line.product = data.attrib.get('trainName', '')
            if not line.product:
                line.product = data.find('./itdNoTrain').attrib['name']

            ridenum = data.attrib.get('trainNum', None)  # overwrites the diva one

            prefix = data.attrib.get('trainType', '')
            line.shortname = prefix+ridenum if prefix else line.name

            # todo: longdistance and similar
            # if result.network == 'ddb':
            #    if result.line[0:2] in ('96', '91'):
            #        result.linetype.name = 'longdistance'
            #    elif result.line[0:2] == '98':
            #        result.linetype.name = 'highspeed'
        else:
            line.product = data.find('./itdNoTrain').attrib['name']
            line.shortname = data.attrib['symbol']
            line.name = '%s %s' % (line.product, line.shortname)

        # origin and destination
        origin = data.attrib.get('directionFrom')
        origin = Stop(self.country, None, origin) if origin else None

        destination = Stop(self.country, None, data.attrib['direction'])
        if data.attrib.get('destID', ''):
            destination._ids[self.name] = int(data.attrib['destID'])

        # route description
        routedescription = data.find('./itdRouteDescText')
        if routedescription is not None:
            line.route = routedescription.text

        return origin, destination, line, rideid, ridenum

    def _parse_trip_point(self, data, walk=False):
        """ Parse a trip Point into a TimeAndPlace (including the Location) """
        city = data.attrib.get('locality', '')
        city = city if city else None

        name = data.attrib.get('nameWO', '')
        name = name if name else None

        # todo – what kind of location is this?
        if walk and data.attrib['area'] == '0':
            location = Address(self.country, city, name)
        else:
            location = Stop(self.country, city, name)
            location._ids[self.name] = int(data.attrib['stopID'])

        result = TimeAndPlace(location)
        result._raws[self.name] = ET.tostring(data, 'utf-8').decode()

        if 'x' in data.attrib:
            result.coords = (float(data.attrib['y']) / 1000000, float(data.attrib['x']) / 1000000)

        # get and clean the platform
        platform = data.attrib['platform']
        if not platform.strip():
            platform = data.attrib['platformName']
        match = re.search(r'[0-9].*$', data.attrib['platformName'])
        result.platform = match.group(0) if match is not None else platform

        # There are three ways to describe the time
        if data.attrib.get('usage', ''):
            # Used for routes (only arrival or departure time)
            times = []
            if data.find('./itdDateTimeTarget'):
                times.append(self._parse_datetime(data.find('./itdDateTimeTarget')))
            if data.find('./itdDateTime'):
                times.append(self._parse_datetime(data.find('./itdDateTime')))

            plantime = None
            livetime = None
            if len(times) > 0:
                plantime = times[0]
            if len(times) == 2 and not walk:
                livetime = times[1]

            if data.attrib['usage'] == 'departure':
                result.departure = RealtimeTime(time=plantime, livetime=livetime)
            elif data.attrib['usage'] == 'arival':
                result.arrival = RealtimeTime(time=plantime, livetime=livetime)

        elif 'countdown' in data.attrib:
            # Used for departure lists
            times = []
            if data.find('./itdDateTime'):
                times.append(self._parse_datetime(data.find('./itdDateTime')))
            if data.find('./itdRTDateTime'):
                times.append(self._parse_datetime(data.find('./itdRTDateTime')))

            plantime = None
            livetime = None
            if len(times) > 0:
                plantime = times[0]
            if len(times) == 2 and not walk:
                livetime = times[1]
            result.departure = RealtimeTime(time=plantime, livetime=livetime)

        else:
            # Also used for routes (arrival and departure time – most times)
            times = []
            for itddatetime in data.findall('./itdDateTime'):
                times.append(self._parse_datetime(itddatetime))

            if len(times) > 0 and times[0] is not None:
                delay = int(data.attrib.get('arrDelay', '-1'))
                delay = timedelta(minutes=delay) if delay >= 0 else None
                result.arrival = RealtimeTime(time=times[0], delay=delay)

            if len(times) > 1 and times[1] is not None:
                delay = int(data.attrib.get('depDelay', '-1'))
                delay = timedelta(minutes=delay) if delay >= 0 else None
                result.departure = RealtimeTime(time=times[1], delay=delay)

        #for genattr in data.findall('./genAttrList/genAttrElem'):
        #	name = genattr.find('name').text
        #	value = genattr.find('value').text
        #	if name == 'platformChange' and value == 'changed':
        #		result.changed_platform = True

        return result
