import aht20
import bmp280
import sys


bmp280 = bmp280.BMP280(0x77, 1)
bmp280.init()

aht20 = aht20.AHT20(0x38, 1)
aht20.init()

while True:
    _ = sys.stdin.readline()
    aht20_humidity, aht20_temperature = aht20.measure()
    line = "sensors,name=aht20 temperature=%.2f,humidity=%.2f\n"
    sys.stdout.write(line % (aht20_temperature, aht20_humidity))
    bmp280_pressure, bmp280_temperature = bmp280.measure()
    line = "sensors,name=bmp280 temperature=%.2f,pressure=%.2f\n"
    sys.stdout.write(line % (bmp280_temperature, bmp280_pressure))
    sys.stdout.flush()
