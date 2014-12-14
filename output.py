#!/usr/bin/env python3
from models import ModelBase, SearchResults
from models import Location, Stop, POI, Address
from models import TimeAndPlace, RealtimeTime
from models import Ride, RideSegment, Line, LineType
from datetime import datetime, timedelta
import string


class PrettyPrint():
    def __init__(self, showDelayedTime=False, width=80):
        self.showDelayedTime = showDelayedTime
        self.width = 80
        
    def formatted(self, obj, indented=0, oneline=False, short=False):
        indent = ' '*indented*2
        output = ''
        header = None
        fields = []
        richfields = []
        if isinstance(obj, Stop) or isinstance(obj, POI) or isinstance(obj, Address):
            header = 'Location'
            fields += ['country', 'city', 'name', 'coords']
            if isinstance(obj, POI):
                header = 'POI'
            elif isinstance(obj, Address):
                header = 'Address'
            elif isinstance(obj, Stop):
                if short:
                    return ((obj.city if obj.city is not None else '')+' '+obj.name).strip()
                header = 'Stop'
                richfields.append(('lines', '\n'+'\n'.join([self.formatted(line, indented+2, True) for line in obj.lines])))
                richfields.append(('rides', '\n'+'\n'.join([self.formatted(ride, indented+2, True) for ride in obj.rides])))
        elif isinstance(obj, LineType):
            return obj.name
        elif isinstance(obj, Line) and short:
            return obj.shortname
        elif isinstance(obj, Line) and oneline:
            direction = ''
            if obj.first_stop is not None or obj.last_stop is not None:
                direction = ' '+(self.formatted(obj.first_stop, 0, True, True)+' ' if obj.first_stop is not None else '')+'→'
                direction += (' '+self.formatted(obj.last_stop, 0, True, True) if obj.last_stop is not None else '')
            return indent+'%s%s (by %s in %s)' % (obj.name, direction, obj.operator, obj.network)
        elif isinstance(obj, RealtimeTime):
            if self.showDelayedTime:
                return obj.livetime.strftime('%H:%M')+('' if not obj.islive else (' (+%d)' % int(obj.delay.total_seconds()/60)))
            else:
                return obj.time.strftime('%H:%M')+('' if not obj.islive else (' +%d' % int(obj.delay.total_seconds()/60)))
        elif isinstance(obj, RideSegment) and oneline:
            direction = (' → '+self.formatted(obj.ride[-1].stop, 0, True, True)) if obj.ride[-1] is not None else ''
            line = indent+self.formatted(obj[0].departure).ljust(10)+' '+obj[0].platform.ljust(5)+' '+self.formatted(obj.ride.line, short=True)+direction
            return line
        
        else:
            header = obj.__class__.__name__
            fields = obj.__dict__.keys()
                
        output = indent+header+'\n'
        for field in fields:
            val = getattr(obj, field)
            if val is None or (type(val) == list and not val):
                continue
            output += indent+' '*2+field+': '
            if isinstance(val, ModelBase):
                output += self.formatted(val, indented+1).lstrip()
            else:
                output += str(val)
            output += '\n'
        for name, value in richfields:
            output += indent+' '*2+name+': '+value+'\n'
        return output