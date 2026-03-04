from machine import I2C, Pin
import time

class LIS3DHTR:
    def __init__(self, i2c, address=0x19):
        self.i2c = i2c
        self.addr = address
        # Sensor konfigurieren
        self.i2c.writeto_mem(self.addr, 0x20, b'\x27')  # CTRL_REG1: Power ON, 10Hz, X/Y/Z enabled
        self.i2c.writeto_mem(self.addr, 0x23, b'\x00')  # CTRL_REG4: Continuous update, +/-2g
        time.sleep(0.1)

    def read_axis(self, low_reg, high_reg):
        # LSB und MSB auslesen
        data0 = self.i2c.readfrom_mem(self.addr, low_reg, 1)[0]
        data1 = self.i2c.readfrom_mem(self.addr, high_reg, 1)[0]
        val = (data1 << 8) | data0
        if val > 32767:
            val -= 65536
        return val

    def read(self):
        scale = 16384 
        x = self.read_axis(0x28, 0x29)/scale
        y = self.read_axis(0x2A, 0x2B)/scale
        z = self.read_axis(0x2C, 0x2D)/scale
        return x, y, z

