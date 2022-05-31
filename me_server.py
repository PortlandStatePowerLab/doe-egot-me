#!/usr/bin/python3
# https://flaviocopes.com/python-http-server/
# https://pythonsansar.com/creating-simple-http-server-python/
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = "localhost"
PORT = 8000

def read_services ():
    try:
        with open('./Outputs To DERMS/OutputtoGSP.xml') as f:
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
            with open('./Outputs To DERMS/OutputtoGSP.xml', 'r') as file:
                self.wfile.write(bytes(file.read(), "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        query_pos = self.path.find('?',0,len(self.path))
        base_path = self.path[:query_pos]
        query_string = self.path[query_pos+1:]
        if (query_pos == -1 and base_path != '/der'):
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(201)
            self.end_headers()

            with open('./RWHDERS Inputs/'+query_string+'.csv','w') as file:
                content_length = int(self.headers['Content-Length'])
                file.write(self.rfile.read(content_length).decode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer(('', 8000), handler)
    print(f"Server started http://{HOST_NAME}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped successfully")
        sys.exit(0)