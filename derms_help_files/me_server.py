#!/usr/bin/python3
# https://flaviocopes.com/python-http-server/
# https://pythonsansar.com/creating-simple-http-server-python/
import re
import os
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = "localhost"
PORT = 8000

def read_services ():
    try:
        with open('./outputs_to_DERMS/OutputtoGSP.xml') as f:
            file = f.read()
    except Exception as e:
        file = e
    return file

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if (self.path == '/services'):
            self.send_response(200)
            self.send_header('Content-type','application/xml')
            self.end_headers()
            with open('./outputs_to_DERMS/OutputtoGSP.xml', 'r') as file:
                self.wfile.write(bytes(file.read(), "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        ders_dir = "./RWHDERS_Inputs/"
        query_pos = self.path.find('?',0,len(self.path))
        base_path = self.path[:query_pos]
        query_string = self.path[query_pos+1:]
        if (query_pos == -1 and base_path != '/der'):
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(201)
            self.end_headers()
            if any(Path(ders_dir).iterdir()) is True:                 # Check if folder not empty
                for der_files in os.listdir(ders_dir):
                    match_cases = re.match(r"DER(\w+)_Bus([^.]+)\.csv",der_files)
                    with open(f'{ders_dir}DER{query_string}_Bus{match_cases.group(2)}') as file:
                        content_length = int(self.headers['Content-Length'])
                        file.write(self.rfile.read(content_length).decode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer(('', 8000), handler)
    print(f"\nServer started http://{HOST_NAME}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped successfully")
        sys.exit(0)
