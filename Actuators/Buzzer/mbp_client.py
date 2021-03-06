#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import configparser
import json
import os
from MenuOption import MenuOption
import requests

################# Configuration #####################
MBP_CLIENT_PROPERTIES_FILE = 'mbp.properties'
SECTION_MBP = 'MBP'
SECTION_MBP_PROPERTY_BROKERHOST = 'brokerHost'
SECTION_MBP_PROPERTY_BROKERPORT = 'brokerPort'
SECTION_MBP_PROPERTY_BROKERTOPIC = 'brokerTopic'
SECTION_MBP_PROPERTY_BROKERACTIONTOPIC = 'brokerActionTopic'
SECTION_COMPONENT = 'Component'
SECTION_COMPONENT_PROPERTY_COMPONENTID = 'componentId'

TOPIC_SEND_MESSAGE_FORMAT = '{"component": "SENSOR", "id": "%s", "value": "%.2f"}'

ACTION_LOG_FILE = 'actions.log'
JSON_PROPERTY_ACTION = 'action'
ACTION_NAME_STOP = 'stop'

YOUR_VM_IP = ""
PORT = "8082" # port in which the webserver of the Buzzer Commands Sensor works
#####################################################

class MBPclient(object):

    def __init__(self, message_callback):
        # Get MQTT broker connection information
        self.__get_mqtt_broker_infos()
        self.message_callback = message_callback
        self.buzzer_status = 0.0
        self.is_active = False

    def connect(self):
        # create the MQTT client instance
        self.client_id = 'mbp-%s' % (self.component_id)
        self.mqtt_client = mqtt.Client(client_id=self.client_id, clean_session=True, userdata=None, protocol=mqtt.MQTTv31)

        # set mqtt client on_connection callback
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message

        self.mqtt_client.connect(self.broker_host, self.broker_port, keepalive=60)

        # Runs a thread in the background to call loop() automatically.
        # This call also handles reconnecting to the broker.
        self.mqtt_client.loop_start()

    def send_data(self, value):
        mbp_message = TOPIC_SEND_MESSAGE_FORMAT % (self.component_id, value)
        self.mqtt_client.publish(topic=self.broker_topic, payload=mbp_message, qos=0, retain=False)
        print('[Sent message]:', mbp_message)

    def subscribe(self, topic):
        self.mqtt_client.subscribe(topic)

    def finalize(self):
        self.mqtt_client.loop_stop()

    def __get_mqtt_broker_infos(self, property_file_name=MBP_CLIENT_PROPERTIES_FILE):
        """Retrieves the MQTT broker information to connect and send data to it."""

        config = configparser.RawConfigParser()
        config.read(property_file_name)
        self.broker_host = config.get(SECTION_MBP, SECTION_MBP_PROPERTY_BROKERHOST)
        self.broker_port = int(config.get(SECTION_MBP, SECTION_MBP_PROPERTY_BROKERPORT))
        self.broker_topic = config.get(SECTION_MBP, SECTION_MBP_PROPERTY_BROKERTOPIC)
        self.broker_action_topic = config.get(SECTION_MBP, SECTION_MBP_PROPERTY_BROKERACTIONTOPIC)
        self.component_id = config.get(SECTION_COMPONENT, SECTION_COMPONENT_PROPERTY_COMPONENTID)

    def _on_connect(self, client, userdata, flags, rc):
        """This callback function is executed when the MQTT client receives a CONNACK response from the MQTT broker."""

        print('[Connected]: client ID', self.client_id, 'result code', str(rc))
        self.subscribe(self.broker_action_topic)

    def _on_message(self, client, userdata, message):

        # Convert message payload to string
        message_string = message.payload.decode(encoding='UTF-8')

        # Open actions log file and append message
        with open(ACTION_LOG_FILE, 'a') as file:
            file.write(message_string)
            file.write('\n')

        msg_json = json.loads(message_string)

        if JSON_PROPERTY_ACTION in msg_json:
            msg_data = msg_json[JSON_PROPERTY_ACTION]
            if (msg_data is not None) and (msg_data.casefold() == ACTION_NAME_STOP.casefold()):
                print('[Exit]: Receive command to exit MBP client')
                self.finalize()
                os._exit(0)

        event_0_value = None
        event_1_value = None
        event_2_value = None

        if "cep_output" in msg_json:

            if "event_0" in msg_json["cep_output"] and "value" in msg_json["cep_output"]["event_0"]:
                event_0_value = float(msg_json["cep_output"]["event_0"]["value"])
            if "event_1" in msg_json["cep_output"] and "value" in msg_json["cep_output"]["event_1"]:
                event_1_value = float(msg_json["cep_output"]["event_1"]["value"])
            if "event_2" in msg_json["cep_output"] and "value" in msg_json["cep_output"]["event_2"]:
                event_2_value = float(msg_json["cep_output"]["event_2"]["value"])
        else:
            print("improper message format")
            return

        #CAMERA
        if event_0_value is not None:
            if event_0_value ==1.0 and self.is_active:
                self.message_callback(MenuOption.ACTIVATE_BUZZER)
                self.buzzer_status = 1.0

        #system command
        if event_1_value is not None:
            if event_1_value == 0.0:
                self.is_active = False
                self.buzzer_status = 0.0
                self.message_callback(MenuOption.DEACTIVATE_BUZZER)
            elif event_1_value == 1.0:
                self.is_active = True

        #buzzer command
        if event_2_value is not None:
            if event_2_value == 0.0:
                self.buzzer_status = 0.0
                self.message_callback(MenuOption.DEACTIVATE_BUZZER)
            elif event_2_value == 1.0:
                self.buzzer_status = 1.0
                self.message_callback(MenuOption.ACTIVATE_BUZZER)

        url = 'http://' + YOUR_VM_IP + ':' + PORT + '/RASPBUZZERSTATUS'
        myobj = '{"value": "%.2f"}' % self.buzzer_status
        headers = {'Content-type': 'application/json'}
        x = requests.post(url, json = {"value": self.buzzer_status}, headers= headers)
