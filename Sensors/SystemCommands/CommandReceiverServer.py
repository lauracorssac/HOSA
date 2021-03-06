import os
from uuid import uuid4
import signal
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from SystemStatusManager import SystemStatusManager
from urllib.parse import urlparse, parse_qs

class CommandReceiverServer(BaseHTTPRequestHandler):

    def __init__(self,manager, notification_manager, token_validation_manager, *args, **kwargs):
        self.message_manager = manager
        self.notification_manager = notification_manager
        self.token_validation_manager = token_validation_manager
        self.codes_json = {
            "PHONESYSTEMSENSOR": self.handle_user_input
        }
        super().__init__(*args, **kwargs)

    def do_GET(self):
        path = self.path[1:]
        print("path", path)
        if path in self.codes_json:
            last_status = SystemStatusManager.get_last_status()
            json_string = '{"value": "%.2f"}' % last_status
            json_data = json_string.encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_data)
        else:
            self.send_response(404)

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

        url_parsed = urlparse(self.path)
        path = url_parsed.path[1:]

        post_body = post_body.decode(encoding='UTF-8')
        msg_json = json.loads(post_body)

        if path in self.codes_json and "value" in msg_json:
            value = float(msg_json["value"])
            print("value", value)
            self.codes_json[path](value)
        else:
            self.respond_with_error(404, None)

    def handle_user_input(self, value):

        url_parsed = urlparse(self.path)
        token = parse_qs(url_parsed.query).get('token', None)

        response_code, response_byte_string = self.token_validation_manager.validate_token(token)

        if response_code != 200:
            self.respond_with_error(response_code, response_byte_string)
            return

        command_code = value
        if command_code == 0.0 or command_code == 1.0:
            self.message_manager.send_data(command_code)
            SystemStatusManager.save_last_status(command_code)
            self.notification_manager.send_notification(command_code)
            self.respond_with_success()
        else:
            self.respond_with_error(400, None)

    def respond_with_success(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'')

    def respond_with_error(self, error_code, message):
        self.send_error(error_code)
        self.end_headers()

        if not message:
            self.wfile.write(b'')
        else:
            self.wfile.write(message)
