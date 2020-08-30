#!/usr/bin/env python3
import argparse
import http.server
from http import HTTPStatus
import pathlib
import shutil
import subprocess
import io

__version__ = "0.1"

class TTSimRequestHandler(http.server.BaseHTTPRequestHandler):
  server_version = "TTSim/" + __version__
  svg_file = pathlib.Path("not_yet_set.svg")
  player = None
  resource_dir = pathlib.Path(__file__).parent.resolve() / "resources"
  def do_GET(self):
    """
    GET requests are used to deliver content
    """
    if (self.path == "/"):
      self._send_index()
    elif (self.path == "/config.json"):
      self._send_config()
    elif (self.path == "/" + self.__class__.svg_file.name):
      self._send_svg()
    else:
      resource_dirs = [
        self.__class__.resource_dir,
        self.__class__.svg_file.parent,
      ]
      self._send_static_resource(resource_dirs)

  def do_POST(self):
    """
    POST requests to "/play" are the API to drive "tttool play"
    """
    content_length = int(self.headers['Content-Length'])
    body = self.rfile.read(content_length).decode()
    try:
      log = self.__class__.player.play(body)
    except Exception as error:
      print(error)
      self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))
    else:
      self.send_response(HTTPStatus.OK)
      self.send_header('Content-type', 'text/plain')
      self.end_headers()
      self.wfile.write(log.encode())

  def _send_index(self):
    try:
      svg_content = self.__class__.svg_file.read_text()
      index_file = self.__class__.resource_dir / "index.html.format"
      index_format = index_file.read_text()
      index_content = index_format.format(
        svg = svg_content
      )
    except FileNotFoundError:
      self.send_error(HTTPStatus.NOT_FOUND)
      return
    self.send_response(HTTPStatus.OK)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(index_content.encode())

  def _send_svg(self):
    try:
      svg_content = self.__class__.svg_file.read_text()
    except FileNotFoundError:
      self.send_error(HTTPStatus.NOT_FOUND)
      return
    self.send_response(HTTPStatus.OK)
    self.send_header('Content-type', 'image/svg+xml')
    self.end_headers()
    self.wfile.write(svg_content.encode())
    
  def _send_static_resource(self, resource_dirs):
    request_path = self.path[1:] # strip of the leading slash to allow concat with the resource dirs
    for candidate in [path / request_path for path in resource_dirs]:
      #print(f"candidate: {candidate}")
      if candidate.exists():
        return self._send(candidate)
    self.send_error(HTTPStatus.NOT_FOUND)
  
  def _send(self, local_path):
    self.send_response(HTTPStatus.OK)
    #self.send_header('Content-type', 'image/svg+xml')
    self.end_headers()
    with local_path.open("rb") as source:
      shutil.copyfileobj(source, self.wfile)
    
class TTSimPlayer:
  tttool = "tttool"
  def __init__(self, gme_file):
    self.gme_file = gme_file

  def start(self):
    self.ttt_proc = subprocess.Popen(
      [self.__class__.tttool, "play", self.gme_file],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      bufsize=0, # if we use a buffer, we cannot read "till we see the promt", as some of this output may has not reached the upper layers.
      #universal_newlines=True # using text streams instead of byte strams seems to *imply* buffering
      )
    print(f"started {self.ttt_proc.args}")
    welcome_text = self._read_till_next_promt()
    print(welcome_text)
    if self.ttt_proc.poll():
      raise "tttool terminated unexpectedly"

  def stop(self):
    self.ttt_proc.terminate()

  def play(self, input_text):
    self.ttt_proc.stdin.write(input_text.encode())
    output_text = self._read_till_next_promt()
    return f"sent:\n{input_text}\n\ngot:\n{output_text}"

  def _read_till_next_promt(self):
    promt = "Next OID touched?" # this is some constant from tttool
    chunk_size = len(promt)
    out = io.StringIO()
    while True:
      # TODO: can we 'select' or some other alternatives for this spin-wait?
      #print(f"read {chunk_size} chars...")
      chunk = self.ttt_proc.stdout.read(chunk_size)
      out.write(chunk.decode())
      if len(chunk) < chunk_size and self.ttt_proc.poll():
        return out.getvalue()
      out_value = out.getvalue()
      if out_value.rfind(promt) >= 0:
        return out_value
      #print(out_value)


def serve(server_address, svg_file, gme_file):
    TTSimRequestHandler.svg_file = pathlib.Path(svg_file)
    TTSimPlayer.tttool = "/Users/jonas/Downloads/tttool-1.9/tttool" # TODO: don't hard code the tool's path
    player = TTSimPlayer(gme_file)
    player.start() # maybe better do this when the index is requested? this would allow "restart on reload"
    TTSimRequestHandler.player = player
    httpd = http.server.HTTPServer(server_address, TTSimRequestHandler)
    print(f"listening on http://{server_address[0]}:{server_address[1]}/")
    print("Press Ctrl-C to quit")
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      pass
    print("\nclosing...")
    httpd.server_close()
    player.stop()

if __name__ == "__main__":
    PORT = 8000
    parser = argparse.ArgumentParser()
    parser.add_argument("svg_file",
      help="Path and filename of the SVG file to serve.")
    parser.add_argument("gme_file",
      help="Path and filename of the GME file to handle the clicked OIDs.")
    args = parser.parse_args()

    server_address = ("localhost", PORT)
    serve(server_address, args.svg_file, args.gme_file)
