
import sys
import os

from BuzzerManager import BuzzerManager
from MenuOption import MenuOption
from IoTGeneralManager import IoTGeneralManager
from mbp_client import MBPclient

buzzer_turned_on = False

def menu_function(menu_option):

    global buzzer_turned_on

    if menu_option == MenuOption.ACTIVATE_BUZZER:
        buzzer_turned_on = True
    elif menu_option == MenuOption.DEACTIVATE_BUZZER:
        buzzer_turned_on = False


def main():

    iot_manager = IoTGeneralManager()
    iot_manager.start()
    buzzer_manager = BuzzerManager()
    mbp_client_instance = MBPclient(menu_function)
    mbp_client_instance.connect()

    while True:
        try:
            if buzzer_turned_on:
                buzzer_manager.buzzAct()
        except:
            error = sys.exc_info()
            print ('Error:', str(error))
            break

    mbp_client_instance.finalize()

if __name__ == '__main__':
    main()
