# Intro

This project outputs I2C sensors data in InfluxDB line protocol format. It integrates nicely with the Telegraf execd input plugin.

Tested on a Raspberry Pi 4 running Ubuntu Groovy attached to a cheap AHT20 + BMP280 sensors board.

# Output

A sample follows.

    sensors,name=aht20 temperature=29.84,humidity=32.33
    sensors,name=bmp280 temperature=30.57,pressure=100723.63

# Installation

Clone the project.

    git clone https://github.com/marcv81/sensors-stats.git
    cd sensors-stats
    virtualenv -p python3 venv
    ./venv/bin/pip3 install -r requirements.txt

Create `/etc/udev/rules.d/99-i2c.rules`.

    SUBSYSTEM=="i2c-dev", OWNER="telegraf", GROUP="telegraf"

Create `/etc/telegraf/telegraf.d/sensors_stats.conf`.

    [[inputs.execd]]
      command = ["/home/ubuntu/sensors-stats/sensors_stats.sh"]
      signal = "STDIN"
      data_format = "influx"

Reboot.
