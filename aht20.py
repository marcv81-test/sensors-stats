import i2cdev
import time


class AHT20(i2cdev.I2C):
    """AHT20 humidity and temperature sensor."""

    def init(self):
        """Initialises the device."""
        if self._is_calibrated():
            return
        self.write(bytes([0xBE, 0x08, 0x00]))
        time.sleep(0.04)

    def measure(self):
        """Measures the humidity and temperature."""
        self._measure_request()
        time.sleep(0.08)
        while self._is_measuring():
            time.sleep(0.02)
        return self._measure_response()

    def _status(self):
        """Reads the status register."""
        self.write(bytes([0x71]))
        return list(self.read(1))[0]

    def _is_calibrated(self):
        """Returns whether the device is calibrated or not."""
        return (self._status() & (1 << 3)) > 0

    def _measure_request(self):
        """Requests a measurement."""
        self.write(bytes([0xAC, 0x33, 0x00]))

    def _is_measuring(self):
        """Returns whether a measurement is in progress or not."""
        return (self._status() & (1 << 7)) > 0

    def _measure_response(self):
        """Reads a measurement."""
        data = list(self.read(7))
        raw = 0
        for i in range(5):
            raw <<= 8
            raw += data[i + 1]
        humidity = (raw >> 20) / pow(2, 20) * 100
        temperature = (raw & 0xFFFFF) / pow(2, 20) * 200 - 50
        return humidity, temperature


if __name__ == "__main__":
    aht20 = AHT20(0x38, 1)
    aht20.init()
    print("RH: %.2f%%, temperature %.2fC" % aht20.measure())
    aht20.close()
