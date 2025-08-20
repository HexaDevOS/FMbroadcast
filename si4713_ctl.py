# si4713_ctl.py
import time
import board
import busio
from adafruit_si4713 import SI4713

class Si4713Controller:
    def __init__(self, freq_mhz: float, tx_power: int = 110):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.radio = SI4713(i2c)
        self.radio.tx_power = max(88, min(115, tx_power))
        self.set_frequency(freq_mhz)
        self.radio.deemphasis = SI4713.DEEMPHASIS_50US
        self.radio.audio_mode = SI4713.AUDIO_ANALOG
        time.sleep(0.2)

    def set_frequency(self, freq_mhz: float):
        self.radio.tx_frequency_khz = int(freq_mhz * 1000)

    def set_power(self, tx_power: int):
        self.radio.tx_power = max(88, min(115, tx_power))

    def shutdown(self):
        try:
            self.radio.tx_power = 88
        except Exception:
            pass
