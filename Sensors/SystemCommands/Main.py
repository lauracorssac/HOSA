from http.server import HTTPServer, BaseHTTPRequestHandler
from mbp_client import MBPclient
from CommandReceiverServer import CommandReceiverServer
from functools import partial
from NotificationManager import NotificationManager
from TokenValidationManager import TokenValidationManager

def main():

    mqtt_manager = MBPclient()
    mqtt_manager.connect()
    notification_manager = NotificationManager()
    token_validation_manager = TokenValidationManager()

    handler = partial(CommandReceiverServer, mqtt_manager, notification_manager, token_validation_manager)
    server = HTTPServer(('', 8084), handler)
    print ("Starting web server on http://localhost:8084/")
    server.serve_forever()


if __name__ == '__main__':
    main()
