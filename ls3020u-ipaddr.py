#!/usr/bin/python3

from ls3020u import LS3020U
import smbus
import time

# Copied from https://stackoverflow.com/revisions/28950776/14
import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

display = LS3020U(smbus.SMBus(1), customFont={'I': 0b0000110, 'P': 0b1110011})

text = '   '.join(['', 'IP'] + get_ip().split('.'))

for i in range(len(text)):
    display.printText(text[i:(i + 2)])
    time.sleep(0.25)

display.printText('')
