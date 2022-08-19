from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from functools import partial
from importlib.resources import path
from pprint import pprint
from ukraine_map import UkraineMap
from urllib.parse import urlparse, parse_qs


class _AlertsHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, map: UkraineMap, *args, **kwargs):
        self._map = map
        self.sys_version = ""
        self.server_version = "Server: Nexus"
        super().__init__(*args, **kwargs)


    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Nothing to see here')


    def do_GET(self):
        parse = urlparse(self.path)
        # query_comps = parse_qs(parse.query)
        path = parse.path.lower().strip("/").split("/")

        if self._handle_as_image_req(path_comps=path):
            return

        self.send_response(418)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'404')

    def _handle_as_image_req(self, path_comps) -> bool:
        try:
            type = path_comps[0]
            if (type != "png") and (type != "jpeg"):
                raise NameError('Unknown type')

            w = int(path_comps[1])
            h = int(path_comps[2])
            self._send_image(width=w, height=h, type=type)
        except BaseException as err:
            pprint(f"Faild to parse path {path_comps}: {err}")
            return False
        except:
            return False


    def _send_image(self, width: int, height: int, type: str):
        image = self._map.get_image(width=width, height=height, type=type)

        self.send_response(200)
        self.send_header('Content-type', f'image/{type}')
        self.end_headers()
        self.wfile.write(image)


class AlertsHTTPServer():
    def __init__(self, host: str, port: int, map: UkraineMap) -> None:
        self._base_url = f"http://{host}:{port}/"

        handler = partial(_AlertsHttpHandler, map)
        self._httpd = HTTPServer((host, port), handler)


    def start(self):
        print(f"Starting server at {self._base_url}")

        try:
            self._httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        print("Stopping server")
        self._httpd.server_close()
