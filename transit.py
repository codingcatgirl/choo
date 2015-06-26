#!/usr/bin/env python3
from models import unserialize_typed
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

try:
    import websockets
except ImportError:
    websockets = None

supported = networks.supported


class TransitInstance():
    allowed_formats = ('json', 'msgpack')

    def __init__(self, default_format=None):
        self.format = default_format
        self.network = None

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
                    self.network = networks.network(data)()
                    return b'ok ' + self.pack(data)
            return b'err unknown network'

        if self.network is None:
            return b'err choose network'

        if command == 'query':
            query = self.unpack(data)

            if query is None:
                return b'err unpack failed'

            try:
                query = unserialize_typed(query)
            except:
                return b'err unserialize failed'

            try:
                print(repr(query))
                result = self.network.query(query)
            except:
                traceback.print_exc()
                return b'err query failed'

            return b'ok ' + self.pack(result.serialize(typed=True))

        return b'err unknown command'

    def pack(self, data):
        if self.format == 'json':
            return json.dumps(data).encode()
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
        instance = TransitInstance()
        while self.rfile.readable():
            data = self.rfile.readline()
            result = instance.handle_msg(data)
            self.wfile.write(result + b'\r\n')


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


@asyncio.coroutine
def ws_handler(websocket, path):
    instance = TransitInstance('json')
    while True:
        data = yield from websocket.recv()
        if data is None:
            break
        result = instance.handle_msg(data.encode()).decode()
        yield from websocket.send(result)


def ws_api():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    start_server = websockets.serve(ws_handler, args.ws_host, args.ws_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


def shell_api():
    instance = TransitInstance()
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
    ws_thread = threading.Thread(target=ws_api)
    ws_thread.daemon = True
    ws_thread.start()
    print('websocket server running on %s:%s' % (args.ws_host, args.ws_port if args.ws_port else  '?'))
    threads.append(ws_thread)

if args.cli:
    print('command line interface running')
    shell_thread = threading.Thread(target=shell_api)
    shell_thread.daemon = True
    shell_thread.start()
    threads.append(shell_thread)

if not threads:
    parser.error('No API selected')

try:
    while True:
        pass
except KeyboardInterrupt:
    pass
