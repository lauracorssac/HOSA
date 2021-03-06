import io
import logging
#import picamera
import socketserver
from threading import Condition
from http import server
from urllib.parse import urlparse, parse_qs

PAGE="""
<html>
<head>
<title>Live Stream</title>
<style>
#bg {{text-align: center}}
#bg img {{width: 100%; max-width:640px; height: auto;}}
</style>
</head>
<body>
<div id="bg">
<img src="stream.mjpg?token={token}"/>
</div>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available'
            #self.buffer.seek(0)
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                if len(self.frame) is not 0:
                    self.condition.notify_all()

                self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):

    def __init__(self, streaming_output, token_validation_manager, *args, **kwargs):
        self.streaming_output = streaming_output
        self.token_validation_manager = token_validation_manager
        super().__init__(*args, **kwargs)

    def respond_with_error(self, error_code, message):
        self.send_error(error_code)
        self.end_headers()

        if not message:
            self.wfile.write(b'')
        else:
            self.wfile.write(message)

    def do_GET(self):

        url_parsed = urlparse(self.path)
        token = parse_qs(url_parsed.query).get('token', None)

        response_code, response_byte_string = self.token_validation_manager.validate_token(token)

        if response_code != 200:
            self.respond_with_error(response_code, response_byte_string)
            return

        token = token[0]

        if url_parsed.path == '/':
            self.send_response(303)
            self.send_header('Location', '/index.html?token=' + token)
            self.end_headers()

        elif url_parsed.path == '/index.html':

            formated_page = PAGE.format(token=token)
            content = formated_page.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif url_parsed.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.streaming_output.condition:
                        self.streaming_output.condition.wait()
                        frame = self.streaming_output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404, b'not-found')
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
