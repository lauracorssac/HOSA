import os
from uuid import uuid4
import signal
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class ImageUploader(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path.endswith('.jpeg') or self.path.endswith('.png'):

            self.send_response(200)
            self.send_header('Content-type','image/png')
            self.end_headers()

            applicationPath = os.getcwd()
            print()
            print("full path", applicationPath + '/images' + self.path)
            print()
            f = open(applicationPath + '/images' + self.path, 'rb')
            self.wfile.write(f.read())
            f.close()
            return
        else:
            self.send_response(200)
            self.end_headers()
