from http.server import HTTPServer, BaseHTTPRequestHandler
from mbp_client import MBPclient
from CommandReceiverServer import CommandReceiverServer
from NotificationManager import NotificationManager
from functools import partial
from TokenValidationManager import TokenValidationManager

def main():

    notification_manager = NotificationManager()
    mqtt_manager = MBPclient()
    mqtt_manager.connect()
    token_validation_manager = TokenValidationManager()

    handler = partial(CommandReceiverServer, mqtt_manager, notification_manager, token_validation_manager)
    server = HTTPServer(('', 8082), handler)
    print ("Starting web server on http://localhost:8082/")
    server.serve_forever()


if __name__ == '__main__':
    main()
