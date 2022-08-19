from http import server
from http.server import HTTPServer, BaseHTTPRequestHandler
# from pprint import pprint

from ukraine_map import UkraineMap
from alerts_parser import AlertsParser
from alerts_server import AlertsHTTPServer

if __name__ == "__main__":
    map = UkraineMap()

    parser = AlertsParser(map)
    parser.start()
    
    server = AlertsHTTPServer(host="0.0.0.0", port=8000, map=map)
    server.start()