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
    sys.stdout.write("sensors,name=aht20,quantity=relative_humidity value=%.2f\n" % aht20_humidity)
    sys.stdout.write("sensors,name=aht20,quantity=temperature value=%.2f\n" % aht20_temperature)
    bmp280_pressure, bmp280_temperature = bmp280.measure()
    sys.stdout.write("sensors,name=bmp280,quantity=pressure value=%.2f\n" % bmp280_pressure)
    sys.stdout.write("sensors,name=bmp280,quantity=temperature value=%.2f\n" % bmp280_temperature)
    sys.stdout.flush()
