#!/usr/bin/env python3
from models import Serializable, unserialize_typed
import sys
import networks
import json
import traceback
import argparse

supported = networks.supported

parser = argparse.ArgumentParser()
parser.add_argument('network', type=str, choices=('networks', ) + networks.supported)
parser.add_argument('search', nargs='?', type=str)
parser.add_argument('--pretty', action='store_true')

args = parser.parse_args()

if args.network == 'networks':
    print(json.dumps(networks.supported))
    sys.exit(0)

network = networks.network(args.network)()

if args.search is None:
    # Interactive Session
    print('Coming Soon')
    sys.exit(0)

if args.search == '-':
    search = sys.stdin.read()
else:
    f = open(args.search)
    search = f.read()
    f.close()

try:
    search = unserialize_typed(json.loads(search))
except:
    traceback.print_exc()
    sys.exit(3)

try:
    result = network.query(search)
except NotImplementedError:
    print('This network does not support this action.')
    sys.exit(4)

if args.pretty:
    print(json.dumps(result.serialize(), indent=2))
else:
    print(json.dumps(result.serialize(), separators=(',', ':')))
