#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

import json
import time
import jwt
import sys
import base64
import requests
from datetime import datetime
from hyper import HTTPConnection, HTTP20Connection

APNS_KEY_ID = '' #E.g.: 4SVKWF123R
APNS_AUTH_KEY_PATH = '' #E.g.: AuthKey_4SVKWF123R.p8
TEAM_ID = ''
ALGORITHM = 'ES256'
BUNDLE_ID = ''
DEVICE_TOKEN = ''

HOST = "" # YOUR VM IP
PORT = 8081

class NotificationManager(object):

    def should_notify(self, old_value, new_value):
        return old_value == 0 and new_value == 1

    def send_notification(self, filename):
        f = open(APNS_AUTH_KEY_PATH)
        secret = f.read()

        path = '/3/device/' + DEVICE_TOKEN

        token = jwt.encode(
            {
                'iss': TEAM_ID,
                'iat': time.time()
            },
            secret,
            algorithm= ALGORITHM,
            headers={
                'alg': ALGORITHM,
                'kid': APNS_KEY_ID,
            }
        )

        request_headers = {
            'apns-expiration': '0',
            'apns-priority': '10',
            'apns-topic': BUNDLE_ID,
            'authorization': 'bearer {0}'.format(token.decode('ascii'))
        }

        payload_data = {
            'aps': {
                "alert": "Danger Alert!",
                "body" : "An intruder might be in your house!",
                "sound": "default",
                "category" : "imageNotificationCategory",
                "mutable-content": "1",
            }
        }

        payload_data["urlImageString"] = 'http://{HOST}:{PORT}/{filename}'.format(HOST= HOST, PORT=PORT, filename=filename)
        print("url string", payload_data["urlImageString"] )
        payload = json.dumps(payload_data).encode('utf-8')

        # Open a connection the APNS server

        # Development
        conn = HTTP20Connection('api.sandbox.push.apple.com:443', force_proto='h2')

        # Send request
        conn.request(
            'POST',
            path,
            payload,
            headers=request_headers
        )
        resp = conn.get_response()
