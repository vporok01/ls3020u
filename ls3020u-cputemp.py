#!/usr/bin/python3

from ls3020u import LS3020U
import atexit
import smbus
from subprocess import check_output
import time

display = LS3020U(smbus.SMBus(1))

atexit.register(lambda: display.printText(''))

while True:
    temp = float(check_output(['vcgencmd', 'measure_temp']).split(b'=', 1)[1].split(b"'", 1)[0])
    status = int(check_output(['vcgencmd', 'get_throttled']).split(b'=', 1)[1].strip(), 16)

    temp = round(temp)
    display.printText(temp)
    if temp >= 60:
        intensity = 0.7
    elif temp >= 40:
        intensity = 0.5
    else:
        intensity = 0.3

    if status & 0x1: # under-voltage detected
        for i in range(2):
            display.setIntensity(intensity / 2)
            time.sleep(0.25)
            display.setIntensity(intensity)
            time.sleep(0.25)
    elif status & 0x4 | status & 0x2: # currently throttled or ARM frequency capped
        display.setIntensity(intensity / 2)
        time.sleep(0.5)
        display.setIntensity(intensity)
    else:
        display.setIntensity(intensity)

    time.sleep(1)
