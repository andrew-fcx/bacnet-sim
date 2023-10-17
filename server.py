from time import sleep
import sys
from random import randint
from device import SimDevice
from constants import *


DEVICE_COUNT = 12 # 11 = BAC0 -> BACC


def update(device, count):
    try:
        device.update_freq()
        device.update_temp()
        device.update_rh()
        device.update_fan_spd()
        if count % FIVE_MIN == 0:
            device.update_fan_spd()
        if count % FIFTEEN_MIN == 0:
            r1 = randint(1, 20)
            device.update_alarm(r1)
            
            r2 = randint(1, 20)
            device.update_enabled(r2)
        if count % EIGHT_HR == 0:
            r3 = randint(1, 20)
            device.update_temp_sp(r3)
            device.update_rh_sp(r3)
            
        if count % SIX_HR == 0:
            r4 = randint(1, 20)
            device.update_fan_spd_sp(r4)

    except Exception as e:
        raise e


if __name__ == "__main__":
    port = START_PORT
    dev_id = START_DEV_ID
    devices = []
    for i in range(DEVICE_COUNT):
        d = SimDevice(str(port), str(dev_id))
        devices.append(d)
        
        port += 1
        dev_id += 1
    
    c = 0
    while True:
        try:
            for dev in devices:
                update(dev, c)
            c += 1
            sleep(SLEEP_DURATION)
        except Exception as e:
            print(e)
            for dev in devices:
                dev.disconnect()
            sys.exit(1)
