#!/usr/bin/python3
"""Measure the liquid level in a bucket and store it in a databse

In order to accumulate a month's data I needed to get this working quickly.
As the system is now live I'm adding unit testing before doing it properly.
This is a v1 hack with attempted minimum impact changes to support unit
testing.
Simply start up 'screen' and invoke it from the command line.
"""

import time
from hc_sr04 import DistanceSensor
try:
    from telegraf.client import TelegrafClient
except ImportError:
    # Unit tests won't run in production envrionment.
    from mock_telegraf import TelegrafClient


def db_handle():
    client = TelegrafClient(host='localhost', port=8094, tags={'src': 'bucket'})
    return client

def get_reading(sensor):
    reading = sensor.get_distance()
    return reading

def map_volume(reading):
    # The 'round' is important to stop Influx declaring the
    # measurement type 'float'. If it does that then it will later
    # reject an attempted insertion of an int.

    # These constants dervied by visual inspection of a best fit line
    # on a Google sheet of the combined calibration data.
    return round((-22.93 * reading) + 2522)

def get_reading_and_volume(sensor, get_volume_func):
    try:
        reading = get_reading(sensor)
        volume = get_volume_func(reading)
    except sensor.InvalidDistanceError:
        reading = 0
        volume = 0

    return reading, volume

def insert_data(client, reading, volume):
    client.metric('lolat', {'reading': reading, 'volume': volume})
    print(f'Sent to db: reading : {reading}, volume: {volume}')

def main():
    """Measure the liquid level in a bucket and store it in a databse."""

    client = db_handle()
    sensor = DistanceSensor()

    with sensor.open():
        while True:
            reading, volume = get_reading_and_volume(sensor, map_volume)
            insert_data(client, reading, volume)
            time.sleep(15 * 60)

if __name__ == "__main__":
    main()
