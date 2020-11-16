#!/usr/bin/python3
"""Measure the liquid level in a bucket and store it in a databse

In order to accumulate a month's data I need to get this working _today_.
This is therefore the quick and dirty, v0 hack.
Simply start up 'screen' and invoke it from the command line.
"""

from hc_sr04 import DistanceSensor
from telegraf.client import TelegrafClient
import time


client = TelegrafClient(host='localhost', port=8094, tags={'src': 'bucket'})
sensor = DistanceSensor()

with sensor.open():
    while True:
        try:
            reading = sensor.get_distance()

            # The 'round' is important to stop Influx declaring the
            # measurement type float as it will then later rejecting
            # an attempted insertion of an int.
            volume = round((-22.93 * reading) + 2522)

            # These constants dervied by visual inspection of a best fit line
            # on a Google sheet of the combined calibration data
        except sensor.InvalidDistanceError as e:
            reading = 0
            volume = 0

        client.metric('lolat', {'reading': reading, 'volume': volume})
        print(f'Sending to db: reading : {reading}, volume: {volume}')

        time.sleep(15 * 60)
