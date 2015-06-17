import socketserver, socket, msgpack, json, traceback

from models import Serializable, unserialize_typed
import networks

class iopacker:
  def pack(self,data): pass
  def unpack(self,data): pass

class msgpacker(iopacker):
  def pack(self,data):
    try:
      return (msgpack.packb(data, use_bin_type=True)+("\r\n".encode()))
    except:
      traceback.print_exc()
      return "ERR msgpacker.pack\r\n".encode()
  def unpack(self,data):
    try:
      return msgpack.unpackb(data, encoding='utf-8')
    except:
      traceback.print_exc()
      return "ERR msgpacker.unpack\r\n".encode()

class jsonpacker(iopacker):
  def pack(self,data):
    return json.dumps(data).encode()
  def unpack(self,data):
    return json.loads(data.decode())

class MyTCPHandler(socketserver.StreamRequestHandler):
  def handle(self):
    self.wfile.write("SELECT network\r\n".encode())
    network=None
    while network==None:
      network=self.rfile.readline().strip().decode()
      if network in networks.supported:
        network=networks.network(network)()
      else:
        self.wfile.write("ERR unsupported network\r\n".encode())
        network=None
    self.wfile.write("SELECT packer\r\n".encode())
    packer=None
    while packer==None:
      packer=self.rfile.readline().strip().decode()
      if packer=="msgpack":
        packer=msgpacker()
      elif packer=="json":
        packer=jsonpacker()
      else:
        packer=None
    while self.rfile.readable():
      self.wfile.write("QUERY\r\n".encode())
      data = self.rfile.readline().strip()
      if not data:
        break
      query=packer.unpack(data)
      try:
        print(query)
        query = unserialize_typed(query)
        try:
          result = network.query(query)
          self.wfile.write("RESULT\r\n".encode())
          self.wfile.write(packer.pack(result.serialize())+("\r\n".encode()))
        except:
          traceback.print_exc()
          self.wfile.write("ERR network.query\r\n".encode())
      except:
        traceback.print_exc()
        self.wfile.write("ERR unserialize_typed\r\n".encode())

class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

if __name__ == "__main__":
  HOST, PORT = "", 1337
  server = MyTCPServer((HOST, PORT), MyTCPHandler)
  server.serve_forever()
