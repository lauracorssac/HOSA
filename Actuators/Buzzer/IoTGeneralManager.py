import RPi.GPIO as GPIO

class IoTGeneralManager(object):
    def __init__(self):
        return

    def start(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

    def stop(self):
        GPIO.cleanup()
