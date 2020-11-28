# LolaT
Liquid Observer: Level, Alert, Trend.

# Description
Take regular distance readings to the surface of a liquid in a tank or bucket.
Use those readings to estimate the volume it contains.
Put this volume estimate into a time series database.
Add graphing to see trends and a configurable
alert meachanism for when the level is too high or low.

# Tech used
* Raspberry Pi and HC-SR04 Ultrasonic Sensor.
* Python, InfluxDB, Grafana.

# Installation
`git clone https://github.com/dougalf/LolaT`

For how to build the hardware see [PiMyLifeUp](https://pimylifeup.com/raspberry-pi-distance-sensor/)

For how to get the Telegraf, InfluxDB and Grafana stack working
see [Michael Schön's blog](https://nwmichl.net/2020/07/14/telegraf-influxdb-grafana-on-raspberrypi-from-scratch/).

For connecting LolaT to Telegraf you'll need
'pip3 install pytelegraf'

The unit tests use pytest.
I'm using a Macbook as my dev env so I developed them there
`sudo -H pip3 install pytest
sudo -H pip3 install pytest-timeout`
They now run as Github actions in a macos-10.5 env when you do a pull request.

# Usage
TDB

# Contributing
Sure, love to hear from you on any topic but
particularly if you have a different hardware sensor.
Mail lolat at dougal dot nl

# Credits
* Gus at PiMyLifeUp.
* Michael Schön for the TIG stack set-up
* Everyone behind Raspberry Pi, Python, InfluxDB, Grafana, Telegraf of course.

# License
GPLv3

# What's in a name
LolaT is a backronym from the Lola T70, my favourite car.
