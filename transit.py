#!/usr/bin/env python3
from models import unserialize_typed, Collection, Collectable
import sys
import networks
import json
import traceback
import socketserver
import argparse
import threading
import asyncio

try:
    import msgpack
except ImportError:
    msgpack = None

websockets = True
try:
    from autobahn.asyncio.websocket import WebSocketServerFactory, WebSocketServerProtocol
except ImportError:
    websockets = False

supported = networks.supported


class TransitInstance():
    allowed_formats = ('json', 'msgpack')

    def __init__(self, write, default_format=None):
        self.format = default_format
        self.byid = False
        self.collection = Collection('session')
        self.network = None
        self.queries = {}
        self.write = write

    def handle_msg(self, msg):
        try:
            return self._handle_msg(msg)
        except:
            traceback.print_exc()
            return b'err internal error (see log/stdout for details)'

    def _handle_msg(self, msg):
        try:
            command, data = msg.strip().split(b' ', 1)
        except:
            return b'err missing argument'

        try:
            command = command.decode()
        except:
            return b'err unknown command'

        if command == 'format':
            try:
                data = data.decode()
            except:
                pass
            else:
                if data in self.allowed_formats:
                    if data == 'msgpack' and msgpack is None:
                        return b'err msgpack is not supported. please install the python3 msgpack module.'

                    self.format = data
                    return b'ok ' + self.pack(self.format)

            return b'err unknown format. allowed formats are ' + repr(self.allowed_formats).encode()

        if self.format is None:
            return b'err choose format'

        if command == 'byid':
            try:
                data = data.decode()
            except:
                pass
            else:
                if data not in ('off', 'on'):
                    return b'err select on or off'
                self.byid = (data == 'on')
                return b'ok ' + self.pack(self.byid)
            return b'err choose format'

        if command == 'get':
            try:
                data = data.decode()
            except:
                pass
            else:
                if data == 'networks':
                    return b'ok ' + self.pack(networks.supported)
            return b'err unknown property'

        if command == 'network':
            try:
                data = data.decode()
            except:
                pass
            else:
                if data in networks.supported:
                    self.network = networks.network(data)(self.collection)
                    return b'ok ' + self.pack(data)
            return b'err unknown network'

        if self.network is None:
            return b'err choose network'

        if command in ('query', 'asyncquery'):
            if command == 'asyncquery':
                if b' ' not in data:
                    return b'err thread id missing'

                queryid, data = data.split(b' ', 1)

            query = self.unpack(data)

            if query is None:
                return b'err unpack failed'

            try:
                query = unserialize_typed(query)
            except:
                traceback.print_exc()
                return b'err unserialize failed'

            if command == 'asyncquery':
                overwrite = queryid in self.queries

                self.queries[queryid] = query
                t = threading.Thread(target=self._thread_query, args=(queryid, query))
                t.daemon = True
                t.start()

                if overwrite:
                    return b'ok ' + self.pack('replaced')
                else:
                    return b'ok ' + self.pack('new')
            else:
                return self._query(query)

        return b'err unknown command'

    def _thread_query(self, queryid, query):
        result = self._query(query)
        if queryid in self.queries and self.queries[queryid] is query:
            self.write(b'async ' + queryid + b' ' + result)
            del self.queries[queryid]

    def abort_queries(self):
        self.queries = {}

    def _query(self, query):
        if isinstance(query, Collectable):
            try:
                found = self.collection.retrieve(query, id_only=True)
                if found is not None:
                    query = found
            except:
                return b'err collection lookup failed'
        try:
            result, ids = self.network.query(query, get_ids=True)
        except NotImplementedError:
            traceback.print_exc()
            return b'err network does not implement this'
        except:
            traceback.print_exc()
            return b'err query failed'

        if self.byid:
            serialized = (self.collection.get_by_ids_serialized(ids), result.serialize(typed=True, refer_by='session'))
        else:
            serialized = result.serialize(typed=True)

        return b'ok ' + self.pack(serialized)

    def pack(self, data):
        if self.format == 'json':
            return json.dumps(data, separators=(',', ':')).encode()
        elif self.format == 'msgpack':
            return msgpack.packb(data, use_bin_type=True) + ('\r\n'.encode())

    def unpack(self, data):
        try:
            if self.format == 'json':
                return json.loads(data.decode())
            elif self.format == 'msgpack':
                return msgpack.unpackb(data, encoding='utf-8')
        except:
            # traceback.print_exc()
            return None


class TransitTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        instance = TransitInstance(lambda r: self.wfile.write(r + b'\r\n'))
        while self.rfile.readable():
            data = self.rfile.readline()
            result = instance.handle_msg(data)
            self.wfile.write(result + b'\r\n')


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)


def ws_api():
    class TransitWebsocketServerProtocol(WebSocketServerProtocol):
        def onConnect(self, request):
            pass

        def onOpen(self):
            self.instance = TransitInstance(lambda r: self.sendMessage(r))

        def onMessage(self, payload, isBinary):
            result = self.instance.handle_msg(payload)
            self.sendMessage(result)

        def connectionLost(self, reason):
            self.instance.abort_queries()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    factory = WebSocketServerFactory('ws://%s:%d' % (args.ws_host, args.ws_port))

    factory.protocol = TransitWebsocketServerProtocol
    factory.setProtocolOptions(allowHixie76=True)

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, args.ws_host, args.ws_port)
    loop.run_until_complete(coro)
    loop.run_forever()


def shell_api():
    instance = TransitInstance(lambda r: sys.stdout.buffer.write(r + b'\r\n'))
    while sys.stdin.buffer.readable():
        data = sys.stdin.buffer.readline()
        result = instance.handle_msg(data)
        sys.stdout.buffer.write(result + b'\r\n')
        sys.stdout.buffer.flush()

parser = argparse.ArgumentParser()
parser.add_argument('--cli', action='store_true', help='enable command line interface')

parser.add_argument('--tcp', action='store_true', help='enable tcp server')
parser.add_argument('--tcp-host', type=str, default='0.0.0.0', help='set address to listen on (default: 0.0.0.0)')
parser.add_argument('--tcp-port', type=int, default=0, help='set tcp port (default: random unused port)')

parser.add_argument('--ws', action='store_true', help='enable websocket server')
parser.add_argument('--ws-host', type=str, default='0.0.0.0', help='set address to listen on (default: 0.0.0.0)')
parser.add_argument('--ws-port', type=int, default=0, help='set tcp port (default: random unused port)')

args = parser.parse_args()

threads = []

if args.tcp:
    tcp_server = ThreadedTCPServer((args.tcp_host, args.tcp_port), TransitTCPHandler)

    ip, port = tcp_server.server_address
    print('tcp server running on %s:%d' % (ip, port))

    tcp_thread = threading.Thread(target=tcp_server.serve_forever)
    tcp_thread.daemon = True
    tcp_thread.start()
    threads.append(tcp_thread)

if args.ws:
    if websockets:
        ws_thread = threading.Thread(target=ws_api)
        ws_thread.daemon = True
        ws_thread.start()
        print('websocket server running on %s:%s' % (args.ws_host, args.ws_port if args.ws_port else '?'))
        threads.append(ws_thread)
    else:
        print('please install the autobahn python module for websocket support.')

if args.cli:
    print('command line interface running')
    shell_thread = threading.Thread(target=shell_api)
    shell_thread.daemon = True
    shell_thread.start()
    threads.append(shell_thread)

if not threads:
    parser.error('No API selected')

try:
    threads[0].join()
except KeyboardInterrupt:
    sys.exit(0)
