
# Copyright 2021 Vladimir Porokhin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

class LS3020U:
    I2C_ADDRESS = 0x20

    REG_INTENSITY = 0x0
    REG_CONTROL1 = 0x1
    REG_CONTROL2 = 0xf
    REG_DIGITS = 0x10

    CTL1_REFRESH = 1 << 0 # shows updated digits on display, applies ctl1 flags from a previous write
    CTL1_LED_TEST = 1 << 4 # enables all segments immediately, no refresh needed
    CTL1_HEX_MODE = 1 << 5 # enables hex decoder, 0 restores direct segment control

    CTL2_RESET1 = 1 << 0 # clears display + everything in ctl1 and ctl2 (including what's sent in ctl2 alongside); intensity is retained
    CTL2_RESET2 = 1 << 1 # same as reset, but allows other flags in ctl2 to be applied
    CTL2_AUTO_REFRESH = 1 << 4 # makes all changes gated by CTL1_REFRESH occur immediately

    SEGMENT_MAPPING = [
        # A  B  C  D  E  F  G
        [ 5, 4, 2, 1, 7, 6, 3], # first digit
        [ 5, 6, 7, 1, 2, 4, 3], # second digit
    ]

    def __init__(self, bus, customFont={}):
        self.bus = bus

        self.font = {
            #      GFEDCBA         GFEDCBA         GFEDCBA         GFEDCBA
            '0': 0b0111111, '1': 0b0000110, '2': 0b1011011, '3': 0b1001111,
            '4': 0b1100110, '5': 0b1101101, '6': 0b1111101, '7': 0b0000111,
            '8': 0b1111111, '9': 0b1101111, 'a': 0b1110111, 'b': 0b1111100,
            'c': 0b1011000, 'd': 0b1011110, 'e': 0b1111001, 'f': 0b1110001,
            '-': 0b1000000, ' ': 0b0000000
        }
        self.font.update(customFont)

        self.ctl1 = 0
        self.ctl2 = 0
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_CONTROL1, self.ctl1)
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_CONTROL2, self.ctl2)

        self._writeDigits([0, 0])
        self._triggerRefreshOptional()

        self.setIntensity(1.0)

    def setIntensity(self, intensity):
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_INTENSITY, int(max(0, min(intensity, 1)) * 0x82))

    def setHexMode(self, enable):
        self.ctl1 = (self.ctl1 & ~self.CTL1_HEX_MODE) | (self.CTL1_HEX_MODE if enable else 0)
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_CONTROL1, self.ctl1)
        self._triggerRefreshOptional()

    def setAutoRefresh(self, enable):
        self.ctl2 = (self.ctl2 & ~self.CTL2_AUTO_REFRESH) | (self.CTL2_AUTO_REFRESH if enable else 0)
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_CONTROL2, self.ctl2)

    def printText(self, text):
        text = '%-2s' % str(text)[0:2]
        self.printSegments([self.font[c] for c in text])

    def printHex(self, value):
        if self.ctl1 & self.CTL1_HEX_MODE:
            self._writeDigits([(value >> 4) & 0xf, value & 0xf])
            self._triggerRefreshOptional()
        else:
            self.printText('%02x' % (value & 0xff))

    def printSegments(self, segments):
        if self.ctl1 & self.CTL1_HEX_MODE:
            self.setHexMode(False)
        if len(segments) < 2:
            segments += [0] * (2 - len(segments))
        else:
            segments = segments[0:2]
        self._writeDigits([self.encodeSegments(s, d) for d, s in enumerate(segments)])
        self._triggerRefreshOptional()

    def encodeSegments(self, segments, digit):
        content = 0
        for segment, shift in enumerate(self.SEGMENT_MAPPING[digit]):
            content |= (segments >> segment & 1) << shift
        return content

    def _writeDigits(self, data):
        assert len(data) == 2
        self.bus.write_i2c_block_data(self.I2C_ADDRESS, self.REG_DIGITS, list(reversed(data)))

    def _writeDigit(self, data, digit):
        assert 0 <= digit <= 1
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_DIGITS + (1 - digit), data)

    def _triggerRefreshOptional(self):
        if self.ctl2 & self.CTL2_AUTO_REFRESH:
            return
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_CONTROL1, self.ctl1 | self.CTL1_REFRESH)
