#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function

import argparse
import io
import re
import time
import sys
import json

import picamera
import subprocess

from mbp_client import MBPclient
from ImageRecognitionManager import ImageRecognitionManager
from CameraStreamer import StreamingOutput
from CameraStreamer import StreamingHandler
from CameraStreamer import StreamingServer
from TokenValidationManager import TokenValidationManager
import threading
from PIL import Image
from datetime import datetime
from functools import partial

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def image_rec_thread_function(image_rec_manager, camera, mqtt_client):

    while True:
        try:
            stream = io.BytesIO()
            capture = camera.capture(stream, format='jpeg', use_video_port=True)
            image = Image.open(stream).convert('RGB').resize((image_rec_manager.input_width, image_rec_manager.input_height), Image.ANTIALIAS)
            personWasDetected = image_rec_manager.analize_image(image)

            if personWasDetected:
                mqtt_client.send_data(1.0)
                imgByteArr = io.BytesIO()
                image.save(imgByteArr, format='jpeg')
                imgByteArr.seek(0)
                imgByteArr = imgByteArr.read()
                mqtt_client.send_image(imgByteArr)

            else:
                mqtt_client.send_data(0.0)

        except:
            error = sys.exc_info()
            print("Ending thread. Please wait")
            print ('Error:', str(error))
            break

def main():

    camera = picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model', help='File path of .tflite file.', required=False, default='detect.tflite')
    parser.add_argument(
    '--threshold',
    help='Score threshold for detected objects.',
    required=False,
    type=float,
    default=0.4)
    args = parser.parse_args()

    mqtt_client = MBPclient()
    mqtt_client.connect()

    image_rec_manager = ImageRecognitionManager(args.model, args.threshold)
    cs1 = threading.Thread(name='consumer1', target=image_rec_thread_function, args=(image_rec_manager, camera, mqtt_client))
    cs1.daemon = True
    cs1.start()

    streaming_output = StreamingOutput()
    token_validation_manager = TokenValidationManager()
    camera.start_recording(streaming_output, format='mjpeg')
    try:
        handler = partial(StreamingHandler, streaming_output, token_validation_manager)
        server = StreamingServer(('', 8000), handler)
        print ("Starting web server on http://localhost:8000/")
        server.serve_forever()
    except:
        error = sys.exc_info()
        print("Ending program. Please wait")
        print ('Error:', str(error))
        camera.close()
        time.sleep(2)
        server.shutdown()
        time.sleep(2)
        mqtt_client.finalize()
        time.sleep(2)

        return

if __name__ == '__main__':
    main()
