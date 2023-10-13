from time import sleep
import sys
from random import randint
from device import SimDevice


def update(device, count):
    try:
        device.update_freq()
        device.update_temp()
        device.update_rh()
        if count % 300 == 0:
            device.update_fan_speed()
        if count % 900 == 0:
            r1 = randint(1, 20)
            device.update_alarm(r1)
            
            r2 = randint(1, 20)
            device.update_enabled(r2)
        if count % 48000 == 0:
            r3 = randint(1, 20)
            device.update_temp_sp(r3)
            
            r4 = randint(1, 20)
            device.update_rh_sp(r4)
    except Exception as e:
        raise e


if __name__ == "__main__":
    d1 = SimDevice('47808', '1110')
    
    c = 0
    while True:
        try:
            update(d1, c)
            c += 1
            sleep(1)
        except Exception as e:
            print(e)
            d1.disconnect()
            sys.exit(1)
