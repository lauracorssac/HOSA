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

APNS_KEY_ID = ''
APNS_AUTH_KEY_PATH = ''
TEAM_ID = ''
ALGORITHM = 'ES256'
BUNDLE_ID = ''
DEVICE_TOKEN = ''

class NotificationManager(object):

    def send_notification(self, value):
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
            'apns-priority': '5',
            'apns-topic': BUNDLE_ID,
            'authorization': 'bearer {0}'.format(token.decode('ascii')),
            'apns-push-type': 'background'
        }

        payload_data = {
            'aps': {
                "content-available": 1
            },
            "id": "PHONESYSTEMSENSOR",
            "value": str(value)
        }
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
