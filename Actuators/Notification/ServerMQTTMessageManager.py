import json
import os

from NotificationManager import NotificationManager
from PersonRecStatusFileManager import PersonRecStatusFileManager
from datetime import datetime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

class ServerMQTTMessageManager(object):

    def __init__(self):

        self.send_next_image = False
        self.is_active = False
        self.notification_manager = NotificationManager()

    def message_handler(self, message):

        if message.topic.startswith("IMAGE_REC"):
            self.handle_person_image(message.payload)

        #person recognition by raspberry
        else:
            new_value_command, new_value_rec = self.get_value_from_payload(message.payload)
            if new_value_command is not None:
                if new_value_command == 1.0:
                    self.is_active = True
                elif new_value_command == 0.0:
                    PersonRecStatusFileManager.save_last_person_rec_status("0.0")
                    self.is_active = False
            if new_value_rec is not None:
                self.handle_person_rec_update(new_value_rec)

    def get_value_from_payload(self, payload):

        message_string = payload.decode(encoding='UTF-8')
        msg_json = json.loads(message_string)

        new_value_command = None
        new_value_rec = None

        if "cep_output" in msg_json:
            if "event_0" in msg_json["cep_output"] and "value" in msg_json["cep_output"]["event_0"]:
                new_value_rec = float(msg_json["cep_output"]["event_0"]["value"])
            if "event_1" in msg_json["cep_output"] and "value" in msg_json["cep_output"]["event_1"]:
                new_value_command = float(msg_json["cep_output"]["event_1"]["value"])
        else:
            print("improper message format")
            return
        return new_value_command, new_value_rec

    def handle_person_rec_update(self, new_value):

        if not self.is_active:
            return

        last_value = PersonRecStatusFileManager.get_last_person_rec_status()
        PersonRecStatusFileManager.save_last_person_rec_status(new_value)

        if self.notification_manager.should_notify(float(last_value), new_value):
            self.send_next_image = True

    def handle_person_image(self, image_data):

        if self.send_next_image:
            now = datetime.now()
            filename = now.strftime("%d-%m-%Y-%H-%M") + ".jpeg"
            target = os.path.join(APP_ROOT, 'images/')
            if not os.path.isdir(target):
                os.mkdir(target)
            destination = "/".join([target, filename])
            f = open(destination, "wb")
            f.write(image_data)
            self.notification_manager.send_notification(filename)
            self.send_next_image = False
