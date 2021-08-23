import i2cdev
import time

# Datasheet: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf


class BMP280(i2cdev.I2C):
    """BMP280 pressure and temperature sensor."""

    def init(self):
        """Initialises the device."""
        self._reset()
        time.sleep(0.001)
        while self._is_resetting():
            time.sleep(0.001)
        self._calibrate()

    def measure(self):
        """Measures the pressure and temperature."""
        self._measure_request()
        time.sleep(0.065)
        while self._is_measuring():
            time.sleep(0.005)
        raw_pressure, raw_temperature = self._measure_response()
        return self._compensate(raw_pressure, raw_temperature)

    def _status(self):
        """Reads the status register."""
        self.write(bytes([0xF3]))
        return list(self.read(1))[0]

    def _reset(self):
        """Resets the device."""
        self.write(bytes([0xE0, 0xB6]))

    def _is_resetting(self):
        """Returns whether a reset is in progress or not."""
        return (self._status() & 1) > 0

    def _calibrate(self):
        """Reads the calibration data."""
        self.write(bytes([0x88]))
        data = list(self.read(24))
        self._calibration = [
            int.from_bytes(data[0:2], "little", signed=False),
            int.from_bytes(data[2:4], "little", signed=True),
            int.from_bytes(data[4:6], "little", signed=True),
            int.from_bytes(data[6:8], "little", signed=False),
            int.from_bytes(data[8:10], "little", signed=True),
            int.from_bytes(data[10:12], "little", signed=True),
            int.from_bytes(data[12:14], "little", signed=True),
            int.from_bytes(data[14:16], "little", signed=True),
            int.from_bytes(data[16:18], "little", signed=True),
            int.from_bytes(data[18:20], "little", signed=True),
            int.from_bytes(data[20:22], "little", signed=True),
            int.from_bytes(data[22:24], "little", signed=True),
        ]

    def _measure_request(self):
        """Requests a measurement in forced mode with the best resolution."""
        self.write(bytes([0xF4, 0b11111101]))

    def _is_measuring(self):
        """Returns whether a measurement is in progress or not."""
        return (self._status() & (1 << 3)) > 0

    def _measure_response(self):
        """Reads a measurement raw data."""
        self.write(bytes([0xF7]))
        data = list(self.read(6))
        raw_pressure = int.from_bytes(data[0:3], "big", signed=False) >> 4
        raw_temperature = int.from_bytes(data[3:6], "big", signed=False) >> 4
        return raw_pressure, raw_temperature

    def _compensate(self, raw_pressure, raw_temperature):
        """Pressure and temperature compensation, based on page 44 of the datasheet."""

        t1, t2, t3, p1, p2, p3, p4, p5, p6, p7, p8, p9 = self._calibration

        # Temperature compensation
        var1 = ((raw_temperature / 16384) - (t1 / 1024)) * t2
        var2 = ((raw_temperature / 131072) - (t1 / 8192)) * ((raw_temperature / 131072) - (t1 / 8192)) * t3
        t_fine = var1 + var2
        temperature = t_fine / 5120

        # Pressure compensation
        var1 = (t_fine / 2) - 64000
        var2 = var1 * var1 * p6 / 32768
        var2 = var2 + (var1 * p5 * 2)
        var2 = (var2 / 4) + (p4 * 65536)
        var1 = ((p3 * var1 * var1 / 524288) + (p2 * var1)) / 524288
        var1 = (1 + (var1 / 32768)) * p1
        p = 1048576 - raw_pressure
        p = (p - (var2 / 4096)) * 6250 / var1
        var1 = p9 * p * p / 2147483648
        var2 = p * p8 / 32768
        pressure = p + ((var1 + var2 + p7) / 16)

        return pressure, temperature


if __name__ == "__main__":
    bmp280 = BMP280(0x77, 1)
    bmp280.init()
    pressure, temperature = bmp280.measure()
    print("pressure: %.2f Pa, temperature: %.2fC" % (pressure, temperature))
    bmp280.close()
