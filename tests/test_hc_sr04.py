#!/usr/bin/python3
"""Unit tests for hc_sr04 sensor."""

import pytest
import time
from threading import Timer
from functools import partial
import mock_GPIO as GPIO
from context import lolat
from hc_sr04 import DistanceSensor

# Python is far from a Real Time OS so don't expect anything like accurate
# timing here. The purpose is to test your driver logic, pin setting etc.
# It is not possible to simulate echo distances by setting input pins after
# appropriate time intervals.

# All distances are in millimeters, all times in seconds.
# Speed of sound in air is about 343m/s = 343,000 mm/s.

def _distance_to_time(distance):
    """Takes a distance in millimeters, returns how long it takes sound
    to travel that distance, in seconds."""
    # distance = speed * time
    # Therefore time = distance / speed
    return distance / 343000

def _time_to_distance(time):
    """Takes a time in seconds, returns how far sound travels in that time,
    in millimeters."""
    # distance = speed * time
    return 343000 * time

def _order_of_magnitude_equal(value, target):
    return value / 10 < target < value * 10

# From the specsheet
# https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
# "IF the signal back, through high level , time of high output IO duration
# is the time from sending ultrasonic to returning. "
#
# So sleep 1 msec to simulate chip doing it's thing of sending out the pulse,
# then set PIN_ECHO HIGH for the given duration.
def pause_then_pulse_input_pin(pin, pulse_duration):
    time.sleep(1/1000)
    GPIO.simulate_input_state_change(pin, GPIO.HIGH)
    timer = Timer(pulse_duration,
                GPIO.simulate_input_state_change,
                [pin, GPIO.LOW])
    timer.start()

def _set_up_callback(mock_sensor, test_distance):
    """Register a callback for when the trigger pin goes high.
    This callback mimics the action of the card on receiving the echo of
    the transmitted sonar pulse."""
    # What to do ...
    _partial_callback_func = partial(pause_then_pulse_input_pin,
                    pin = mock_sensor.PIN_ECHO,
                    pulse_duration = _distance_to_time(test_distance))
    # ... when to do it
    GPIO.register_event_callback(
                    mock_sensor.PIN_TRIGGER,
                    GPIO.RISING,
                    _partial_callback_func)

@pytest.mark.timeout(1)
def test_board_setup():
    mock_sensor = DistanceSensor()
    with mock_sensor.open():
        assert GPIO.getmode() == GPIO.BOARD
        assert GPIO.is_output(mock_sensor.PIN_TRIGGER)
        assert GPIO.output_is_low(mock_sensor.PIN_TRIGGER)
        assert GPIO.is_input(mock_sensor.PIN_ECHO)

@pytest.mark.timeout(3)
def test_sensor_1m():
    """Simulate object very roughly 1m away"""
    test_distance = 1000 # 1m is 1000mm
    mock_sensor = DistanceSensor()
    with mock_sensor.open():
        _set_up_callback(mock_sensor, test_distance)
        returned_distance = mock_sensor.get_distance()
    assert _order_of_magnitude_equal(returned_distance, test_distance)

@pytest.mark.timeout(3)
def skip_test_sensor_too_close_exception():
    """Simulate object too close to the sensor. Verify Exception is thrown."""
    # Couldn't get this to work (due to Python multitask clock granularity?)
    # Any distance too short and the trigger event happens before
    # the code under test has time to listen for it.
    # Any longer and the Exception isn't raised.
    test_distance = 20
    mock_sensor = DistanceSensor()
    with mock_sensor.open():
        _set_up_callback(mock_sensor, test_distance)
        with pytest.raises(mock_sensor.InvalidDistanceError):
            mock_sensor.get_distance()

@pytest.mark.timeout(3)
def test_sensor_too_far_exception():
    """Simulate object too far from the sensor. Verify Exception is thrown."""
    test_distance = 10 * 1000 # 10m
    mock_sensor = DistanceSensor()
    with mock_sensor.open():
        _set_up_callback(mock_sensor, test_distance)
        with pytest.raises(mock_sensor.InvalidDistanceError):
            returned_distance = mock_sensor.get_distance()

@pytest.mark.timeout(1)
def test_board_cleanup():
    mock_sensor = DistanceSensor()
    with mock_sensor.open():
        pass
    assert GPIO.getmode() == GPIO.UNKNOWN

# TBD:
# * More complex tests to exercise the 'drop highest and lowest and average
#   the rest' code.
#   Tricky because we need to change the callback duration mid test.
#   Callbacks to set callbacks anyone?
# * Test to check we don't trigger because of a stray echo from a previous test.
#   Again tricky because of Python's timing inaccuracy.
