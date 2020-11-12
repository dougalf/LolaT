# hc_sr04.py
#!/usr/bin/python3
"""Library for measuring distance using the HC-SR04 ultrasonic sensor.

API calls:
- setup: initialise the board.
- teardown: tidy up when done.
- get_distance: provide an estimate, in mm, of distance to the nearest object.

API Raises:
- InvalidDistanceError: sensor indicates object too close or too far.

For alternate hardware simply implement equivalent versions of the above.
"""


# GPIO code from Gus at PiMyLifeUp
# https://pimylifeup.com/raspberry-pi-distance-sensor/

import RPi.GPIO as GPIO
import time
from contextlib import contextmanager

# ultrasonic ranging module HC - SR04 spec sheet
# https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
# says "2cm - 400cm non-contact measurement function,
# the ranging accuracy can reach to 3mm"
# However testing
# (see https://github.com/dougalf/LolaT/wiki/HC-SR04-sensor-calibration)
# suggests 30mm is the lowest that will be returned and that results
# aren't particulary accurate.

# This module could therefore be improved by attempting a propoer
# calibration of the sensor and creating a mapping
# function "when sensor indicates this, actual distance is that".
# However for LolaT we are going to calibrate the output of this to a volume
# of liquid so the intermeidate step of length does not have to be accurate.

# all distances are in millimeters, all times in seconds


class DistanceSensor():
    class Error(Exception):
        """Base class for Exceptions raised by this library"""
        pass


    class InvalidDistanceError(Error):
        """Sensor return indicates an out of spec distance."""
        def __init__(self, message): 
            self.message = message 


    def __init__(self):
        # Set range of valid readings.
        # (See specsheet and testing comments above).
        # Allowing a 10% margin at either side.
        self.DIST_MIN = 27
        self.DIST_MAX = 4400


    @contextmanager
    def open(self):
        """Do one time sensor set-up, call in 'with' block, tidy up when done"""
        self.PIN_TRIGGER = 7
        self.PIN_ECHO = 11

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)
        try:
            yield self
        finally:
            GPIO.cleanup()
    
    
    def _get_pulse_round_trip_time(self):
        """Send an ultrasonic pulse. Return the time it takes to come back."""

        # Avoid possibility of triggering prematurely from a stray
        # pulse from a previous call to this func.
        # Recommendation of 60msec is equivalent to an echo from ~10m away.
        time.sleep(60 / 1000)  # = 60msec, taken from datasheet.

        # Tell board to send ultrasonic burst.
        GPIO.output(self.PIN_TRIGGER, GPIO.HIGH)
        time.sleep(10 / 1000000)  # = 10usec, taken from datasheet.
        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)

        # (Phyiscal sensor design should prevent this but) don't want
        # the rx to get triggered by the pulse going out in the tx direction
        # ie before it bounces back. Wait for echo pin to go quiet.
        #
        # Could do this with a rising edge callback but seems like overkill.
        start_wait_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 0:
            start_wait_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 1:
            echo_rx_time = time.time()
        round_trip_time = echo_rx_time - start_wait_time
        return round_trip_time
    

    def _get_distance(self):
        """Send an ultrasonic pulse. Use the round trip time taken
        to calculate (and return) the distance to the nearest thing.

        Raises:
            InvalidDistanceError if round trip time leads to a calculated
            distance that is too large or small.
        """

        # distance = speed * time
        # Speed of sound in air is about 343m/s = 343000 mm/s obviously.
        # (Also available in scipy.constants but currently adding the
        # module dependancy is overkill.)
        # Time is for signal to go there and back so divide by 2.
        distance = 343000 * self._get_pulse_round_trip_time() / 2
        if distance < self.DIST_MIN:
            raise self.InvalidDistanceError('Nothing in range of sensor?')
        elif distance > self.DIST_MAX:
            raise self.InvalidDistanceError('Something too close to sensor?')
        else:
            return distance
    
    
    def get_distance(self):
        """Return an estimate in mm of distance to the object nearest to the
        ultrasonic sensor. Rounded to the nearest millimeter.

        Takes 5 readings, drops the highest and lowest, and returns an average
        of the rest.

        Raises:
            InvalidDistanceError if any of the readings indicate a distance
            that is out of spec.
        """

        NUM_READINGS = 5
    
        readings = []
        for _ in range(NUM_READINGS):
            try:
                readings.append(self._get_distance())
            except self.InvalidDistanceError:
                # In testing I never saw 4 good readings and 1 invalid one.
                # Therfore don't just ignore one and try and get 4 valid
                # readings. Something serious is wrong, pass it up.
                raise
    
        # drop (potential) outliers then return average, to the nearest mm
        ret_val = round((sum(readings) - min(readings) - max(readings))/3)
        return ret_val
