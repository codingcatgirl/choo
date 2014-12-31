#!/usr/bin/env python3
from models import ModelBase
from output import PrettyPrint
import sys
import networks
import json
import traceback

argv = sys.argv[1:]
argc = len(argv)

methods = {
    'get_stop': ('Stop', ),
    'get_stop_rides': ('Stop', )
}

if argc == 1 and argv[0] == 'networks':
    print(json.dumps(networks.supported))
    sys.exit(0)
elif argc == 1 and argv[0] == 'methods':
    print(json.dumps(methods))
elif argc > 1:
    if argv[0] not in networks.supported:
        print('Unknown network.')
        sys.exit(2)
    network = networks.network(argv[0])()
    if argv[1] not in methods:
        print('Unknown method.')
        sys.exit(2)
    method = argv[1]
    argv = argv[2:]

    myformat = 'nojson'
    if argv[0] in ('--nojson', '--json', '--json-noraws'):
        myformat = argv[0][2:]
        argv = argv[1:]

    maxc = len(methods[method])
    minc = len([item for item in methods[method] if type(item) == str or None not in item])
    if len(argv) > maxc or len(argv) < minc:
        print('Invalid Argument count for this method.')
        sys.exit(2)

    args = []
    for arg in argv:
        if arg == '-':
            data = ''
            for line in sys.stdin:
                data += line
        else:
            f = open(arg)
            data = f.read()
            f.close()
        args.append(data)

    try:
        args = [ModelBase.unserialize(json.loads(item)) for item in args]
    except:
        traceback.print_exc()
        sys.exit(3)

    try:
        result = getattr(network, method)(*args)
    except NotImplementedError:
        print('This method is not supported by this network.')
        sys.exit(4)

    if myformat == 'nojson':
        p = PrettyPrint()
        print(p.formatted(result))
    elif myformat == 'json-noraws':
        print(json.dumps(result.serialize(['noraws'])))
    else:
        print(json.dumps(result.serialize()))
else:
    print('  transit-cli networks')
    print('  transit-cli methods')
    print('  transit-cli <network> <method> [ --pretty | --nopretty ] <arguments>')
    print('Invalid Syntax.')
    sys.exit(2)
