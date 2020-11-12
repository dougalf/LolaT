# calibrate_HC-SR04_sensor.py
#!/usr/bin/python3
"""Code used to test performance and behaviour of HC-SR04 ultrasonic sensor.

Invoke from the command line.

Tells the sensor to transmit an ultrasonic pulse and measures the time it
takes to receive it back, having bounced off something in the enviornment.
This time is converted to distance (in meters, rounded to millimeter
accuracy) and the result printed.  3 such measurements are made, after
one another and the average is also output.

You can use this code to investigate sensor performance and behaviour by
placing objects a known distance in front of it, introducing them from
the side to measure the point at which the distance changes, determining the
minimum and max distances and so on.

An example result set can be found at
https://github.com/dougalf/LolaT/wiki/HC-SR04-sensor-calibration
"""

# Code adapted with thanks from Gus at PiMyLifeUp
# https://pimylifeup.com/raspberry-pi-distance-sensor/
# Dougal Featherstone lolat@dougal.nl 2020-11-04

import RPi.GPIO as GPIO
import time

# Units are meters and seconds throughout.

SPEED_OF_SOUND = 343	# m/s

# ultrasonic ranging module HC - SR04 spec sheet
# https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
# gives "2cm - 400cm non-contact measurement function,
# the ranging accuracy can reach to 3mm"

# trigger pin high signal duration to start ranging
TRIGGER_DURATION = 10 / 1000000	# 10usec

# when looping avoid possibility of triggering prematurely from a stray
# pulse from a previous tx. This delay is equivalent to an echo coming back
# from ~10m away.
MIN_CYCLE_TIME = 60 / 1000	# 60msec

# looping makes sense eg to take 3 readings in an attempt to increase
# the accuracy from 3mm

try:
    GPIO.setmode(GPIO.BOARD)

    PIN_TRIGGER = 7
    PIN_ECHO = 11

    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    # from Gus's original code, not sure where he got it from.
    print("Waiting for sensor to settle")
    time.sleep(2)

    print( "Calculating distance")
    num_readings = 3
    running_total = 0

    for _ in range(num_readings):
        # tell board to send burst
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        time.sleep(TRIGGER_DURATION)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        # phyiscal hardwardware set-up should prevent this but don't want
        # the rx to get triggered by the pulse in the tx direction ie before
        # it bounces back. Wait for echo pin to go quiet
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()

        # spec says pin high time gives "input TTL with a range in proportion".
        # Does that imply we can also get a max distance? Well, whatever we are
        # only interested in the earliest time the pulse comes back.
        pulse_duration = pulse_end_time - pulse_start_time	# in seconds

        # distance = speed * time
        # Time is for signal to go there and back so divide by 2
        distance = round(SPEED_OF_SOUND * pulse_duration / 2, 3)	# in m, to mm accuracy
        print("Distance: ", int(distance * 1000),"mm")
        running_total += distance

        time.sleep(MIN_CYCLE_TIME)

    print("Average distance: ", int(round(running_total * 1000 / num_readings)), "mm")

finally:
    GPIO.cleanup()
