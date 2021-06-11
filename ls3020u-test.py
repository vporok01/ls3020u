#!/usr/bin/python3

from ls3020u import LS3020U
import smbus, time

display = LS3020U(smbus.SMBus(1))
display.setAutoRefresh(True)

display.setIntensity(0.5)

for i in range(16):
    display.printText('%2x' % i)
    time.sleep(0.15)

time.sleep(0.5)

display.setHexMode(True)
for i in range(16):
    display.printHex(i << 4)
    time.sleep(0.15)

time.sleep(0.5)

for i in range(16):
    display.setIntensity(1 - (i / 16.0))
    time.sleep(0.05)

display.printText('')
