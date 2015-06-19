#!/usr/bin/env python3
from models import unserialize_typed
import sys
import networks
import json
import traceback
import argparse

supported = networks.supported

parser = argparse.ArgumentParser()
parser.add_argument('network', type=str, choices=('networks', ) + networks.supported, help='network/API to use. “networks” lists all available networks')
parser.add_argument('query', nargs='?', type=str, help='representation of a Searchable or Searchable.Request')
parser.add_argument('--input', type=str, choices=('json', 'msgpack'), default='json', help='input format (default: json)')
parser.add_argument('--output', type=str, choices=('json', 'prettyjson', 'msgpack'), default='json', help='output format (default: json)')

args = parser.parse_args()

if args.network == 'networks':
    result = networks.supported
else:
    network = networks.network(args.network)()

    if args.query is None:
        # Interactive Session
        print('Coming Soon')
        sys.exit(0)

    if args.input == 'json':
        if args.query == '-':
            query = sys.stdin.read()
        else:
            f = open(args.query)
            query = f.read()
            f.close()

        try:
            query = json.loads(query)
        except:
            traceback.print_exc()
            sys.exit(3)

    elif args.input == 'msgpack':
        try:
            import msgpack
        except:
            raise ImportError('Please install: pip install msgpack-python')

        if args.query == '-':
            query = sys.stdin.buffer.read()
        else:
            f = open(args.query, 'rb')
            query = f.read()
            f.close()

        try:
            query = msgpack.unpackb(query, encoding='utf-8')
        except:
            traceback.print_exc()
            sys.exit(3)

    try:
        query = unserialize_typed(query)
    except:
        traceback.print_exc()
        sys.exit(4)

    try:
        result = network.query(query)
    except NotImplementedError:
        print('This network does not support this action.')
        sys.exit(5)

serialized = None if result is None else result.serialize(typed=True)

if args.output == 'json':
    print(json.dumps(serialized, separators=(',', ':')))
elif args.output == 'prettyjson':
    print(json.dumps(serialized, indent=2))
elif args.output == 'mspack':
    try:
        import msgpack
    except:
        raise ImportError('Please install: pip install msgpack-python')
    sys.stdout.buffer.write(msgpack.packb(serialized, use_bin_type=True))
