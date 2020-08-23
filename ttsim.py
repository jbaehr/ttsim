#!/usr/bin/env python3
import argparse
import http.server
from http import HTTPStatus
import pathlib
import shutil

__version__ = "0.1"

class TTSimRequestHandler(http.server.BaseHTTPRequestHandler):
  server_version = "TTSim/" + __version__
  svg_file = pathlib.Path("not_yet_set.svg")
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
    self.send_error(HTTPStatus.NOT_IMPLEMENTED, "still on the TODO-List")

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
    

def serve(server_address, svg_file, gme_file):
    TTSimRequestHandler.svg_file = pathlib.Path(svg_file)
    httpd = http.server.HTTPServer(server_address, TTSimRequestHandler)
    print(f"listening on http://{server_address[0]}:{server_address[1]}/")
    print("Press Ctrl-C to quit")
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      pass
    print("\nclosing...")
    httpd.server_close()

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
