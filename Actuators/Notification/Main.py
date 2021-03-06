from http.server import HTTPServer, BaseHTTPRequestHandler
from mbp_client import MBPclient
from ImageUploader import ImageUploader
from PersonRecStatusFileManager import PersonRecStatusFileManager
from NotificationManager import NotificationManager
from ServerMQTTMessageManager import ServerMQTTMessageManager

import sys
import signal

def main():

    PersonRecStatusFileManager.save_last_person_rec_status("0.0")

    mqtt_manager = ServerMQTTMessageManager()
    mqtt_client = MBPclient(mqtt_manager.message_handler)
    mqtt_client.connect()

    server = HTTPServer(('', 8081), ImageUploader)
    print ("Starting web server on http://localhost:8081/")
    server.serve_forever()

if __name__ == '__main__':
    main()