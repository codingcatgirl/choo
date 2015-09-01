#!/usr/bin/env python3
from ..models import Searchable
from ..models import Location, Stop, POI, Address
from ..models import TimeAndPlace, Platform, RealtimeTime
from ..models import Trip, Ride, RideSegment, Coordinates, TicketList, TicketData
from ..models import Line, LineType, LineTypes, Way, WayType, WayEvent
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from .base import API
import requests
import re
import math


class EFA(API):
    name = 'efa'
    base_url = None
    country_by_id = ()
    ifopt_platforms = False
    place_id_safe_stop_id_prefix = None
    train_station_suffixes = {}
    train_station_lines = LineTypes(('train', 'urban'))
    encoding = 'ISO-8859-1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cities = {}

    def _get_location(self, location):
        if not isinstance(location, Stop):
            raise NotImplementedError
        result, now = self._get_stop_rides(location)
        if not isinstance(result, location.__class__):
            result = None
        return result, now

    def _search_locations(self, location):
        if type(location) != Location.Request:
            raise NotImplementedError
        return self._stop_finder_request(location)

    def _search_trips(self, triprequest):
        return self._trip_request(triprequest)

    # Internal methods start here
    def _get_stop_rides(self, stop):
        return self._departure_monitor_request(stop)

    def _post(self, endpoint, data):
        text = requests.post(self.base_url + endpoint, data=data).text
        open('dump.xml', 'w').write(text)
        return ET.fromstring(text)

    def _convert_location(self, location, wrap=''):
        """ Convert a Location into POST parameters for the EFA Requests """
        myid = location.id if location.source == self.name else None

        city = location.city.encode(self.encoding) if location.city is not None else None
        name = location.name.encode(self.encoding) if location.name is not None else None

        model = location.Model if isinstance(location, Location.Request) else location.__class__

        if name is None:
            if location.coords is not None:
                r = {'type': 'coord', 'name': '%.6f:%.6f:WGS84' % (reversed(location.coords))}
            else:
                r = {'type': 'stop', 'place': city, 'name': ''}
        elif issubclass(model, Stop):
            if myid is not None:
                r = {'type': 'stop', 'place': None, 'name': str(myid)}
            elif location.ifopt is not None and location.country is not None:
                r = {'type': 'stop', 'place': None,
                     'name': '%s:%s:%s' % ((location.country, ) + location.ifopt)}
            else:
                r = {'type': 'stop', 'place': city, 'name': name}
        elif issubclass(model, Address):
            r = {'type': 'address', 'place': city, 'name': name}
        elif issubclass(model, POI):
            if myid is not None:
                r = {'type': 'poiID', 'name': str(myid)}
            else:
                r = {'type': 'poi', 'place': city, 'name': name}
        elif issubclass(model, Location):
            r = {'type': 'any', 'place': city, 'name': name if name else None}
        else:
            raise NotImplementedError

        if r['place'] is None:
            del r['place']

        if wrap:
            r = {wrap % n: v for n, v in r.items()}

        return r

    def _trip_request(self, triprequest: Trip.Request):
        """ Searches connections/Trips; Returns a SearchResult(Trip) """
        now = datetime.now()

        assert triprequest.walk_speed in ('slow', 'normal', 'fast')

        linetypes = triprequest.linetypes
        if linetypes is None:
            linetypes = LineTypes()

        departure = triprequest.departure
        arrival = triprequest.arrival

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

        max_changes = triprequest.max_changes
        if max_changes is None:
            max_changes = 9

        post = {
            'changeSpeed': triprequest.walk_speed,
            'command': '',
            'coordOutputFormat': 'WGS84',
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
            'maxChanges': max_changes,
            'name_via': '',  # .decode('utf-8').encode('iso-8859-1'),
            'nextDepsPerLeg': 1,
            'place_via': '',  # decode('utf-8').encode('iso-8859-1'),
            'ptOptionsActive': 1,
            'requestID': 0,
            'routeType': 'LEASTTIME',
            # {'speed':'LEASTTIME', 'waittime':'LEASTINTERCHANGE', 'distance':'LEASTWALKING'}[select_interchange_by],
            'sessionID': 0,
            'type_via': 'stop',
            'useRealtime': 1,
            'outputFormat': 'XML'
        }

        # if use_realtime: post['useRealtime'] = 1

        if 'train' in linetypes:
            post['inclMOT_0'] = 'on'

        if 'train.longdistance.highspeed' in linetypes:
            post['lineRestriction'] = 400
        elif 'train.longdistance' in linetypes:
            post['lineRestriction'] = 401
        else:
            post['lineRestriction'] = 403

        for linetype, number in (('urban', '1'), ('metro', '2'), ('metro', '3'),
                                 ('tram', '4'), ('bus.city', '5'), ('bus.regional', '6'),
                                 ('bus.express', '7'), ('suspended', '8'), ('ship', '9'),
                                 ('dialable', '10'), ('other', '11')):
            if linetype in linetypes:
                post['inclMOT_' + number] = 'on'

        if triprequest.wayduration_origin or triprequest.wayduration_destination:
            post['useProxFootSearch'] = 1

        waytypes = {'walk': 100, 'bike': 101, 'car': 104, 'taxi': 105}
        post['trITDepMOT'] = waytypes[str(triprequest.waytype_origin)]
        post['trITArrMOT'] = waytypes[str(triprequest.waytype_destination)]

        post['trITDepMOTvalue%d' % post['trITDepMOT']] = triprequest.wayduration_origin.total_seconds() // 60
        post['trITArrMOTvalue%d' % post['trITArrMOT']] = triprequest.wayduration_destination.total_seconds() // 60

        if triprequest.with_bike:
            post['bikeTakeAlong'] = 1

        if triprequest.wheelchair:
            post['wheelchair'] = 1

        if triprequest.low_floor_only:
            post['lowPlatformVhcl'] = 1

        if not triprequest.allow_solid_stairs:
            post['noSolidStairs'] = 1

        if not triprequest.allow_escalators:
            post['noEscalators'] = 1

        if not triprequest.allow_elevators:
            post['noElevators'] = 1

        post.update(self._convert_location(triprequest.origin, '%s_origin'))
        post.update(self._convert_location(triprequest.destination, '%s_destination'))

        xml = self._post('XSLT_TRIP_REQUEST2', post)
        servernow = datetime.strptime(xml.attrib['now'], '%Y-%m-%dT%H:%M:%S')

        data = xml.find('./itdTripRequest')

        results = Trip.Results(self._parse_routes(data.find('./itdItinerary/itdRouteList')))
        results.origin = self._parse_odv(data.find('./itdOdv[@usage="origin"]'))
        results.destination = self._parse_odv(data.find('./itdOdv[@usage="destination"]'))

        return results, servernow

    def _stop_finder_request(self, stop):
        """ Searches a Stop; Returns a SearchResult(Stop) """
        post = {
            'language': 'de',
            'outputFormat': 'XML',
            'coordOutputFormat': 'WGS84',
            'locationServerActive': 1,
            # 'regionID_sf': 1, // own region
            'SpEncId': 0,
            'odvSugMacro': 'true',
            'useHouseNumberList': 'true',
        }
        post.update(self._convert_location(stop, '%s_sf'))

        xml = self._post('XSLT_STOPFINDER_REQUEST', post)
        servernow = datetime.strptime(xml.attrib['now'], '%Y-%m-%dT%H:%M:%S')

        data = xml.find('./itdStopFinderRequest')

        results = self._parse_odv(data.find('./itdOdv'))
        if type(results) != list:
            return stop.Model.Results([results] if isinstance(results, stop.Model) else []), servernow

        results = [result for result in results if isinstance(result[0], stop.Model)]

        if isinstance(stop, Searchable.Request) and stop.limit is not None:
            results = results[:stop.limit]

        return stop.Model.Results(results, scored=True), servernow

    def _departure_monitor_request(self, stop: Stop, time: datetime=None):
        """ Fills in Stop.rides; Can Return A SearchResult(Stop) without rides. """
        if time is None:
            time = datetime.now()

        post = {
            'command': '',
            'coordOutputFormat': 'WGS84',
            'imparedOptionsActive': 1,
            'itdDateDay': time.day,
            'itdDateMonth': time.month,
            'itdDateYear': time.year,
            'itdTimeHour': time.hour,
            'itdTimeMinute': time.minute,
            'language': 'de',
            'lsShowTrainsExplicit': 1,
            'mode': 'direct',
            'outputFormat': 'XML',
            'locationServerActive': 1,
            'itOptionsActive': 1,
            'ptOptionsActive': 1,
            'includeCompleteStopSeq': 1,
            'depType': 'stopEvents',
            'useRealtime': 1,
            'stateless': 1,
            'requestID': 0,
            'sessionID': 0
        }
        post.update(self._convert_location(stop, '%s_dm'))

        xml = self._post('XSLT_DM_REQUEST', post)
        servernow = datetime.strptime(xml.attrib['now'], '%Y-%m-%dT%H:%M:%S')

        data = xml.find('./itdDepartureMonitorRequest')

        stop = self._parse_odv(data.find('./itdOdv'))

        if type(stop) == list:
            return Stop.Results(stop)

        lineslist = data.find('./itdServingLines')

        if lineslist is not None:
            rlines = []
            lines = lineslist.findall('./itdServingLine')
            for line in lines:
                origin, destination, line, ridenum, ridedir, canceled = self._parse_mot(line)
                line.first_stop = origin
                line.last_stop = destination
                # line.low_quality = True
                rlines.append(line)
            stop.lines = Line.Results(rlines)

        departureslist = data.find('./itdDepartureList')
        stop.rides = self._parse_departures(departureslist, stop, servernow)

        train_station = False
        for line in stop.lines:
            if line.linetype in self.train_station_lines:
                train_station = True
                break

        self._make_train_station(stop, train_station)

        return stop, servernow

    def _get_country(self, i):
        for s, country in self.country_by_id:
            if i.startswith(s):
                return country
        return None

    def _process_stop_city(self, stop, cityid):
        if (stop.id is None or self.place_id_safe_stop_id_prefix is None or
                not str(stop.id).startswith(self.place_id_safe_stop_id_prefix)):
            return

        if cityid in self.cities:
            country, city = self.cities[cityid]
            if stop.city is None:
                stop.city = city
                if city is not None and stop.name.startswith(city + ' '):
                    stop.name = stop.name[len(city) + 1:]
            elif city is None:
                self.cities[cityid] = (country, stop.city)
                city = stop.city

            if stop.country is None:
                stop.country = country
            elif country is None:
                self.cities[cityid] = (stop.country, city)
                country = stop.country
        else:
            self.cities[cityid] = (stop.country, stop.city)

    def _make_train_station(self, stop, force=False):
        if not isinstance(stop, Stop):
            return

        if not force:
            for suffix in self.train_station_suffixes:
                if stop.name.endswith(suffix):
                    break
            else:
                return

        name = stop.name
        for suffix, replacement in self.train_station_suffixes.items():
            if name.endswith(suffix):
                name = name[:-len(suffix)] + replacement
        name = name.strip()
        stop.train_station_name = (
            '%s %s' % ('' if stop.city is None or name.startswith(stop.city) else stop.city, name)
        ).strip()

    def _parse_stop_line(self, data):
        """ Parse an ODV line (for example an AssignedStop) """
        city = data.attrib.get('locality', data.attrib.get('place', ''))
        city = city if city else None

        name = data.text
        stop = Stop(country=self._get_country(data.attrib['stopID']),
                    city=city, name=name, id=int(data.attrib['stopID']))

        gid = data.attrib.get('gid', '').split(':')
        if len(gid) == 3 and min(len(s) for s in gid):
            stop.country = 'de'
            stop.ifopt = ':'.join((gid[1], gid[2]))

        self._make_train_station(stop)

        if 'x' in data.attrib:
            stop.coords = Coordinates(float(data.attrib['y']) / 1000000, float(data.attrib['x']) / 1000000)

        return stop

    def _parse_odv(self, data):
        """ Parse an ODV (OriginDestinationVia) XML node """
        odvtype = data.attrib['type']
        results = []

        # Place.city
        p = data.find('./itdOdvPlace')
        cityid = None
        if p.attrib['state'] == 'empty':
            city = None
        elif p.attrib['state'] != 'identified':
            if p.attrib['state'] == 'list':
                pe = p.find('./odvPlaceElem')
                for item in pe:
                    location = Location(None, city=item.text)
                    results.append(location)
            return results
        else:
            pe = p.find('./odvPlaceElem')
            cityid = pe.attrib.get('placeID')
            city = pe.text

        # Location.name
        n = data.find('./itdOdvName')
        if n.attrib['state'] == 'empty':
            if city is not None:
                location = Location(None, city)
                results.append(location)
            return results
        elif n.attrib['state'] != 'identified':
            if n.attrib['state'] == 'list':
                ne = n.findall('./odvNameElem')
                results = [self._name_elem(item, city, cityid, odvtype) for item in ne]
                results.sort(key=lambda odv: odv[1], reverse=True)
            return results
        else:
            ne = n.find('./odvNameElem')
            result = self._name_elem(ne, city, cityid, odvtype)[0]
            near_stops = []
            for near_stop in data.findall('./itdOdvAssignedStops/itdOdvAssignedStop'):
                stop = self._parse_stop_line(near_stop)
                if stop != result:
                    near_stops.append(stop)
            result.near_stops = Stop.Results(near_stops)
            return result

    def _name_elem(self, data, city, cityid, odvtype):
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
            location = Stop(city=city, name=name)
        elif odvtype == 'poi':
            location = POI(city=city, name=name)
        elif odvtype == 'street':
            location = Address(city=city, name=name)
        elif odvtype in ('singlehouse', 'coord', 'address'):
            location = Address(city=city, name=name)
            location.street = data.attrib['streetName'] if 'streetName' in data.attrib else None
            location.number = data.attrib['buildingNumber'] if 'buildingNumber' in data.attrib else None
            if location.number is None:
                location.number = data.attrib['houseNumber'] if 'houseNumber' in data.attrib else None
            location.name = '%s %s' % (location.street, location.number)
        else:
            raise NotImplementedError('Unknown odvtype: %s' % odvtype)

        # IDs can come in different ways… Sometimes this is the only way to determine the Location type…
        stopid = data.attrib.get('stopID', '')
        myid = data.attrib.get('id', '')
        if stopid:
            if location is None:
                location = Stop(city=city, name=name)
            if isinstance(location, Stop):
                location.country = self._get_country(stopid)
                location.id = int(stopid)
        elif myid:
            if location is None:
                location = POI(city=city, name=name)
            location.country = self._get_country(myid)
            location.id = int(myid)
        elif location is None:
            # Still no clue about the Type? Well, it's an Address then.
            location = Address(city=city, name=name)

        # This is used when we got more than one Location
        score = int(data.attrib.get('matchQuality', 0))

        # Coordinates
        if 'x' in data.attrib:
            location.coords = Coordinates(float(data.attrib['y']) / 1000000, float(data.attrib['x']) / 1000000)

        self._make_train_station(location)

        if cityid:
            self._process_stop_city(location, int(cityid))

        return location, score

    def _parse_departures(self, data, stop, servernow):
        """ Parses itdDeparture into a List of RideSegment """
        servernow.replace(second=0, microsecond=0)
        results = []
        departures = data.findall('./itdDeparture')
        for departure in departures:
            # Get Line Information
            origin, destination, line, ridenum, ridedir, canceled = self._parse_mot(departure.find('./itdServingLine'))

            if departure.find('./genAttrList/genAttrElem[value="HIGHSPEEDTRAIN"]') is not None:
                line.linetype = LineType('train.longdistance.highspeed')
            elif departure.find('./genAttrList/genAttrElem[value="LONG_DISTANCE_TRAINS"]') is not None:
                line.linetype = LineType('train.longdistance')

            # if ridenum is None:
            #     ridedata = departure.find('./itdServingTrip')
            #     if ridedata is not None:
            #         ridenum = ridedata.attrib.get('tripCode', None)
            #         if ridenum is not None:
            #             ridenum = ridenum.strip()

            # Build Ride Objekt with known stops
            ride = Ride(line, ridenum)
            ride.direction = ridedir
            ride.canceled = canceled

            train_line = line.linetype in self.train_station_lines

            # todo: take delay and add it to next stops
            mypoint = self._parse_trip_point(departure, train_line=train_line)

            before_delay = None
            if mypoint.arrival:
                before_delay = mypoint.arrival.delay
            after_delay = None
            if mypoint.departure:
                after_delay = mypoint.departure.delay

            delay = None
            if departure.find('./itdServingLine/itdNoTrain'):
                delay = departure.find('./itdServingLine/itdNoTrain').attrib.get('delay', None)
                if delay is not None:
                    delay = timedelta(minutes=delay)

            if delay is not None:
                if ((mypoint.arrival and servernow < mypoint.arrival.livetime) or
                        (mypoint.departure and servernow < mypoint.departure.livetime)):
                    before_delay = delay
                else:
                    after_delay = delay

            prevs = False
            for pointdata in departure.findall('./itdPrevStopSeq/itdPoint'):
                point = self._parse_trip_point(pointdata, train_line=train_line)
                if point is not None:
                    if before_delay is not None:
                        if (point.arrival is not None and point.arrival.delay is None and
                                point.arrival.time + before_delay >= servernow):
                            point.arrival.delay = before_delay
                        if (point.departure is not None and point.departure.delay is None and
                                point.departure.time + before_delay >= servernow):
                            point.departure.delay = before_delay
                    prevs = True
                    ride.append(point)

            pointer = ride.append(mypoint)

            onwards = False
            for pointdata in departure.findall('./itdOnwardStopSeq/itdPoint'):
                point = self._parse_trip_point(pointdata, train_line=train_line)
                if point is not None:
                    if after_delay is not None:
                        if (point.arrival is not None and point.arrival.delay is None and
                                point.arrival.time + after_delay >= servernow):
                            point.arrival.delay = after_delay
                        if (point.departure is not None and point.departure.delay is None and
                                point.departure.time + after_delay >= servernow):
                            point.departure.delay = after_delay
                    onwards = True
                    ride.append(point)

            if not prevs and not onwards:
                ride.prepend(None)
                if origin is not None:
                    ride.prepend(TimeAndPlace(Platform(origin)))

                ride.append(None)
                if destination is not None:
                    ride.append(TimeAndPlace(Platform(destination)))

            # Return RideSegment from the Station we depart from on
            results.append(ride[pointer:])
        return Ride.Results(results)

    def _parse_routes(self, data):
        """ Parses itdRoute into a Trip """
        trips = []
        routes = data.findall('./itdRoute')
        for route in routes:
            trip = Trip()
            interchange = None
            for routepart in route.findall('./itdPartialRouteList/itdPartialRoute'):
                part = self._parse_routepart(routepart)
                if interchange is not None:
                    if isinstance(part, RideSegment):
                        interchange.destination = part[0].platform
                    else:
                        interchange.destination = part[0].origin
                trip._parts.append(part)

                interchange = self._parse_interchange(routepart)
                if isinstance(part, RideSegment):
                    if interchange is not None:
                        interchange.origin = part[-1].platform
                        trip._parts.append(interchange)
                else:
                    if interchange is not None:
                        part.events = interchange.events
                        interchange = None

            ticketlist = TicketList()
            tickets = route.find('./itdFare/itdSingleTicket')
            if tickets:
                authority = tickets.attrib['net']
                ticketlist.single = TicketData(authority,
                                               tickets.attrib['unitsAdult'],
                                               float(tickets.attrib['fareAdult']),
                                               float(tickets.attrib['fareChild']))
                ticketlist.bike = TicketData(authority,
                                             tickets.attrib['unitsBikeAdult'],
                                             float(tickets.attrib['fareBikeAdult']),
                                             float(tickets.attrib['fareBikeChild']))
                ticketlist.currency = tickets.attrib['currency']
                ticketlist.level_name = tickets.attrib['unitName']
                for ticket in tickets.findall('./itdGenericTicketList/itdGenericTicketGroup'):
                    t = TicketData()
                    name = ticket.find('./itdGenericTicket[ticket="TICKETTYPE"]/value')
                    if name is None or not name.text:
                        continue

                    authority = ticket.find('./itdGenericTicket[ticket="TARIFF_AUTHORITY"]/value')
                    if authority is not None and authority.text:
                        t.authority = authority.text

                    level = ticket.find('./itdGenericTicket[ticket="FARE_CATEGORY"]/value')
                    if level is not None and level.text:
                        t.level = level.text

                    prices = []
                    adult = ticket.find('./itdGenericTicket[ticket="TICKET_ID_ADULT"]/value')
                    if adult is not None and adult.text:
                        price = ticket.find('./itdGenericTicket[ticket="FARE_ADULT"]/value')
                        if price is not None and price.text:
                            prices.append(float(price.text))

                    child = ticket.find('./itdGenericTicket[ticket="TICKET_ID_CHILD"]/value')
                    if child is not None and child.text:
                        price = ticket.find('./itdGenericTicket[ticket="FARE_CHILD"]/value')
                        if price is not None and price.text:
                            prices.append(float(price.text))

                    if not prices:
                        continue

                    t.price = prices[0]
                    if len(prices) == 2:
                        t.price_child = prices[1]
                    ticketlist.other[name.text] = t
                trip.tickets = ticketlist

            trips.append(trip)

        return trips

    def _parse_interchange(self, data):
        """ Parses an optional interchange path of a itdPartialRoute into a Way """
        info = data.find('./itdFootPathInfo')
        if info is None:
            return None

        way = Way()
        way.duration = timedelta(minutes=int(info.attrib.get('duration')))

        path = []
        for coords in data.findall('./itdInterchangePathCoordinates/itdPathCoordinates/'
                                   '/itdCoordinateBaseElemList/itdCoordinateBaseElem'):
            path.append(Coordinates(int(coords.find('y').text) / 1000000, int(coords.find('x').text) / 1000000))

        if path:
            way.path = path

        events = []
        for event in data.findall('./itdFootPathInfo/itdFootPathElem'):
            name = event.attrib['type'].lower()
            direction = event.attrib['level'].lower()
            if name in ('elevator', 'escalator', 'stairs') and direction in ('up', 'down'):
                events.append(WayEvent(name, direction))
        way.events = events

        return way

    def _parse_routepart(self, data):
        """ Parses itdPartialRoute into a RideSegment or Way """
        points = [self._parse_trip_point(point) for point in data.findall('./itdPoint')]

        path = []
        for coords in data.findall('./itdPathCoordinates/itdCoordinateBaseElemList/itdCoordinateBaseElem'):
            path.append(Coordinates(int(coords.find('y').text) / 1000000, int(coords.find('x').text) / 1000000))

        motdata = self._parse_mot(data.find('./itdMeansOfTransport'))

        if motdata is None or data.attrib['type'] == 'IT':
            waytype = {
                '98': 'walk',
                '99': 'walk',
                '100': 'walk',
                '101': 'bike',
                '104': 'car',
                '105': 'taxi'
            }[data.find('./itdMeansOfTransport').attrib['type']]
            # 98 = gesichter anschluss

            way = Way(WayType(waytype), points[0].stop, points[1].stop)
            way.distance = data.attrib.get('distance')
            if way.distance is not None:
                way.distance = float(way.distance)
            duration = data.attrib.get('timeMinute', None)
            if duration is not None:
                way.duration = timedelta(minutes=int(duration))
            if path:
                way.path = path
            return way

        else:
            origin, destination, line, ridenum, ridedir, canceled = motdata

            if data.find('./genAttrList/genAttrElem[value="HIGHSPEEDTRAIN"]') is not None:
                line.linetype = LineType('train.longdistance.highspeed')
            elif data.find('./genAttrList/genAttrElem[value="LONG_DISTANCE_TRAIN"]') is not None:
                line.linetype = LineType('train.longdistance')

            train_line = line.linetype in self.train_station_lines

            # Build Ride Objekt with known stops
            ride = Ride(line, ridenum)
            ride.canceled = canceled
            ride.direction = ridedir
            for infotext in data.findall('./infoTextList/infoTextListElem'):
                ride.infotexts.append(infotext)

            first = None
            last = None
            waypoints = False
            if data.find('./itdStopSeq'):
                new_points = [self._parse_trip_point(point, train_line=train_line)
                              for point in data.findall('./itdStopSeq/itdPoint')]
                if not new_points or new_points[0].stop != new_points[0].stop:
                    new_points.insert(0, points[0])
                if new_points[-1].stop != points[1].stop:
                    new_points.append(points[1])
                points = new_points
                waypoints = True

            for p in points:
                if not waypoints and first is None:
                    ride.append(None)
                pointer = ride.append(p)
                if first is None:
                    first = pointer
            last = pointer

            if origin is not None:
                if origin != ride[0].stop:
                    ride.prepend(None)
                    ride.prepend(TimeAndPlace(Platform(origin)))
            else:
                ride.prepend(None)

            if destination is not None:
                if destination != ride[-1].stop:
                    ride.append(None)
                    ride.append(TimeAndPlace(Platform(destination)))
            else:
                ride.append(None)

            segment = ride[first:last]
            paths = self._split_path(path, [p.platform.coords for p in segment])[:-1]
            for i, point in segment.items():
                if not paths:
                    break
                segment.ride._paths[i] = paths.pop(0)
            return segment

    def _split_path(self, totalpath, points):
        pointi = [None for point in enumerate(points)]

        # Find Points that are too close to not be right
        for i, coord in enumerate(totalpath):
            for j, point in enumerate(points):
                d = (abs(point.lat - coord.lat) ** 2 + abs(point.lon - coord.lon) ** 2) ** 0.5
                if d < 0.0002 and (pointi[j] is None or pointi[j][2] > d):
                    pointi[j] = (i, 0, d)

        # For the rest, find a place between to points
        lastcoord = None
        for i, coord in enumerate(totalpath):
            if lastcoord is None or lastcoord == coord:
                continue

            for j, point in enumerate(points):
                if pointi[j] is not None:
                    continue

                # print([coord.serialize(), point.serialize(), lastcoord.serialize()])
                if 2.84 < abs(math.atan2(coord.lat - point.lat, coord.lon - point.lon) -
                              math.atan2(lastcoord.lat - point.lat, lastcoord.lon - point.lon)) < 3.44:
                    pointi[j] = (i, 1)
                    break

        # And if still some points are not found on the line, just take the closest
        for i, coord in enumerate(totalpath):
            for j, point in enumerate(points):
                d = (abs(point.lat - coord.lat) ** 2 + abs(point.lon - coord.lon) ** 2) ** 0.5
                if pointi[j] is None or (pointi[j][1] == 2 and pointi[j][2] > d):
                    pointi[j] = (i, 2, d)

        if None in pointi:
            return []

        pointitest = [p[0] for p in pointi]
        if sorted(pointitest) != pointitest:
            # We found the points in the wrong order – so this is bullshit, return nothing
            return []

        paths = []
        for i, data in reversed(list(enumerate(pointi))):
            if data[1] == 1:
                paths.insert(0, totalpath[data[0]:])
                totalpath = totalpath[:data[0]]
            else:
                paths.insert(0, totalpath[data[0]:])
                totalpath = totalpath[:data[0] + 1]

        return paths

    def _parse_datetime(self, data):
        """ Create a datetime from itdDate and itdTime """
        d = data.find('./itdDate').attrib
        t = data.find('./itdTime').attrib

        # -1 means nope, there is no time known
        if d['weekday'] == '-1' or d['day'] == '-1' or t['minute'] == '-1':
            return None

        # convert time – the EFA API likes to talk about 24:00, so we have to correct that.
        result = datetime(int(d['year']), int(d['month']), int(d['day']), min(int(t['hour']), 23), int(t['minute']))
        if int(t['hour']) == 24:
            result += timedelta(hours=1)
        return result

    def _parse_mot(self, data):
        """ Parse a itdServingLine Node into something nicer """
        line = Line()

        if 'motType' not in data.attrib:
            return None

        # determine Type
        mottype = int(data.attrib['motType'])
        line.linetype = LineType(('train.local', 'urban', 'metro', 'urban', 'tram',
                                  'bus.city', 'bus.regional', 'bus.express', 'suspended',
                                  'ship', 'dialable', 'other')[mottype])

        train = data.find('./itdTrain')
        if train is not None:
            line.linetype = LineType('train.longdistance.highspeed' if train.get('type') in ('ICE', 'THA')
                                     else 'train.longdistance')

        traintype = data.attrib.get('trainType')
        if traintype is not None:
            line.linetype = LineType('train.longdistance.highspeed' if traintype in ('ICE', 'THA')
                                     else 'train.longdistance')

        train_line = line.linetype in self.train_station_lines

        # general Line and Ride attributes
        diva = data.find('./motDivaParams')
        ridedir = None
        if diva is not None:
            line.network = diva.attrib['network']
            line.id = ':'.join((diva.attrib['network'], diva.attrib['line'], diva.attrib['supplement'],
                                diva.attrib['direction'], diva.attrib['project']))
            ridedir = diva.attrib['direction'].strip()
            if not ridedir:
                ridedir = None

        ridenum = data.attrib.get('tC', None)
        if ridenum is None:
            ridenum = data.attrib.get('key', None)

        op = data.find('./itdOperator')
        if op is not None:
            line.operator = op.find('./name').text

        # We behave different for trains and non-trains
        if mottype == 0:
            line.name = data.attrib['symbol']
            line.product = data.attrib.get('trainName', '')

            if not line.product:
                line.product = data.attrib.get('productName', '')

            if not line.product:
                line.product = data.find('./itdNoTrain').attrib['name']

            if 'trainNum' in data.attrib:
                ridenum = data.attrib['trainNum']  # overwrites the diva one

            prefix = data.attrib.get('trainType', '')
            line.shortname = (prefix + ridenum) if prefix else line.name

            if not line.shortname:
                train = data.find('./itdTrain')
                if train is not None:
                    line.shortname = train.attrib['type']

            if not line.name:
                line.name = line.shortname
        else:
            line.product = data.attrib.get('productName', '')
            if not line.product:
                line.product = data.find('./itdNoTrain').attrib['name']
            line.shortname = data.attrib['symbol']
            line.name = '%s %s' % (line.product, line.shortname)

        if data.find('./itdNoTrain'):
            canceled = data.find('./itdNoTrain').attrib.get('delay', '') == '-9999'
        else:
            canceled = None

        # origin and destination
        origin = data.attrib.get('directionFrom')
        origin = Stop(name=origin) if origin else None
        self._make_train_station(origin, train_line)

        destination = data.attrib.get('destination', data.attrib.get('direction', None))
        destination = Stop(name=destination) if destination else None
        if data.attrib.get('destID', ''):
            destination.country = self._get_country(data.attrib['destID'])
            destination.id = int(data.attrib['destID'])
        self._make_train_station(destination, train_line)

        # route description
        routedescription = data.find('./itdRouteDescText')
        if routedescription is not None:
            line.route = routedescription.text

        return origin, destination, line, ridenum, ridedir, canceled

    def _parse_trip_point_name(self, data):
        # todo: this can be better
        city = data.attrib.get('locality', data.attrib.get('place', ''))
        city = city if city else None

        name = data.attrib.get('nameWO', '')
        name = name if name else None

        if name is None:
            name = data.attrib.get('name', '')
            if ', ' in name and (city is None or name.startswith(city)):
                city, name = name.split(', ', 1)

        if city is None:
            tmp = data.attrib.get('stopName', '')
            if not tmp:
                tmp = data.attrib.get('name', '')
                if ', ' in tmp:
                    city, name = tmp.split(', ', 1)
                elif tmp.endswith(' ' + name):
                    tmp = tmp[:-len(name)].strip()
                    if tmp:
                        city = tmp

                if city is None:
                    name = tmp

            elif city is None and tmp.endswith(' ' + name):
                tmp = tmp[:-len(name)].strip()
                if tmp:
                    city = tmp

        return city, name

    def _parse_trip_point(self, data, walk=False, train_line=False):
        """ Parse a trip Point into a TimeAndPlace (including the Location) """
        city, name = self._parse_trip_point_name(data)

        if data.attrib['area'] == '' and data.attrib['stopID'] == '0':
            return None

        # todo – what kind of location is this?
        if walk and data.attrib['area'] == '0':
            location = Address(city=city, name=name)
        else:
            location = Stop(country=self._get_country(data.attrib['stopID']), city=city, name=name)
            location.id = int(data.attrib['stopID'])
            self._make_train_station(location, train_line)

            cityid = data.attrib.get('placeID')
            if cityid:
                self._process_stop_city(location, int(cityid))

        # get and clean the platform
        platform = data.attrib['platform']
        if not platform.strip():
            platform = data.attrib['platformName']
        match = re.search(r'[0-9].*$', data.attrib['platformName'])
        platform = match.group(0) if match is not None else platform
        if not platform:
            platform = None

        full_platform = data.attrib['platformName']
        if not full_platform:
            full_platform = platform
        if platform == full_platform and 'pointType' in data.attrib:
            full_platform = '%s %s' % (data.attrib['pointType'], platform)
        if not full_platform:
            full_platform = None

        platform = Platform(stop=location, name=platform, full_name=full_platform)
        if full_platform is not None:
            platform.id = ':'.join((str(location.id), data.attrib['area'], data.attrib['platform']))

        ifopt = data.attrib.get('gid', '').split(':')
        if len(ifopt) == 3:
            location.country = ifopt[0]
            location.ifopt = ':'.join(ifopt)
            ifopt = data.attrib.get('pointGid', '').split(':')

        if len(ifopt) == 5 and str(location.id).endswith(ifopt[2]):
            if location.ifopt is None:
                location.country = ifopt[0]
                location.ifopt = ':'.join(ifopt[:3])

            if full_platform is not None:
                platform.ifopt = ':'.join(ifopt)

        result = TimeAndPlace(platform)

        if data.attrib.get('x'):
            platform.coords = Coordinates(float(data.attrib['y']) / 1000000, float(data.attrib['x']) / 1000000)

        # for genattr in data.findall('./genAttrList/genAttrElem'):
        #  	name = genattr.find('name').text
        # 	value = genattr.find('value').text
        # 	if name == 'platformChange' and value == 'changed':
        # 		result.changed_platform = True

        self._parse_trip_point_time(data, result, walk)
        return result

    def _parse_trip_point_time(self, data, point, walk=False):
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
                point.departure = RealtimeTime(time=plantime, livetime=livetime)
            elif data.attrib['usage'] == 'arival':
                point.arrival = RealtimeTime(time=plantime, livetime=livetime)

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
            point.departure = RealtimeTime(time=plantime, livetime=livetime)

        else:
            # Also used for routes (arrival and departure time – most times)
            times = []
            for itddatetime in data.findall('./itdDateTime'):
                times.append(self._parse_datetime(itddatetime))

            if not [t for t in times if t is not None]:
                point.passthrough = True

            if len(times) > 0 and times[0] is not None:
                delay = int(data.attrib.get('arrDelay', '-1'))
                delay = timedelta(minutes=delay) if delay >= 0 else None
                point.arrival = RealtimeTime(time=times[0], delay=delay)

            if len(times) > 1 and times[1] is not None:
                delay = int(data.attrib.get('depDelay', '-1'))
                delay = timedelta(minutes=delay) if delay >= 0 else None
                point.departure = RealtimeTime(time=times[1], delay=delay)
