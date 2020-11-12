#!/usr/bin/python3
#/usr/bin/python
"""Generate a JSON file look-up table for sensor reading <> liquid volume.

Guide the user in pouring liquid into the bucket to generate sample points.
Output is a JSON file of these mappings.

See issue #23 for feature ideas to improve this.
"""

import os
import json
from hc_sr04 import DistanceSensor


class _NoMoreInputException(Exception):
    """User indicates they are done with the calibration proceess."""
    pass


def _open_file():
    """Open the JSON file.

    Asks for confirm before overwriting.  Bails on all other errors.
    Let the user fix via the command line.

    Returns:
        The file handle

    Raises:
        FileExistsError if the user doesn't want to over-write an existing file.
    """
    # Words reverse order between this file name and its output. Oh well.
    # Issue #22 will fix this string being hardocded.
    MAPPING_FILE_NAME = 'bucket_calibration.json'
    try:
        f = open(MAPPING_FILE_NAME, 'x')
    except FileExistsError as e:
        if input('File exists. Overwrite? [N|y] ') == 'y':
            f = open(MAPPING_FILE_NAME, 'w')
        else:
            raise e
    # There are plenty other file systme errors, let Python handle them.
    # Will get fixed with #22 and #23, particularly if filename becomes
    # a user input.
    return f


def _get_input_vol(message, default_vol: int = 0):
    """Ask the user for how much liquid they are adding to the bucket.

    Insist it be an integer.
    If they give an empty string use the passed default value

    Raises:
        _NoMoreInputException when the user has done adding liquid

    Returns:
        int - volume of liquid added. Can be negative.
    """

    while True:
        input_vol = input(f"""{message},
\tor just 'enter' for same as last time ({default_vol}),
\tor 'q' to write file and finish. """)
        if input_vol == '':
            return default_vol
        if input_vol == 'q':
            raise _NoMoreInputException
        try:
            return int(input_vol)
        except ValueError:
            print("Couldn't parse that input. Please try again.")


def _get_distance_or_quit(sensor):
    """Wrapper to allow retries or graceful finish in the case of sensor Error

    Returns: distance

    Raises: _NoMoreInputException when user chooses to stop.
    """
    while True:
        try:
            reading = sensor.get_distance()
            break
        except sensor.InvalidDistanceError as e:
            print(e.message)
            print('Check sensor / liquid level then press enter to try again.')
            if input("\tOr enter 'q' to write file and finish. ") == 'q':
                raise _NoMoreInputException
    return reading


def main():
    """Create a JSON file containing sensor readings v actual liquid volume.

    Check the output file is writeable.

    Have the user pour liquid into their bucket. Have them enter the added
    volume. Get a reading from the sensor. Append that to our output list.
    Repeat.

    Write the file.
    """

    sensor = DistanceSensor()
    # Use 'with' to do sensor setup and teardown in a tidy way.
    # We only need the file handle when we are done but better to be
    # sure we can open the output file for writing _before_ the user
    # does all their bucket filling.
    with sensor.open(), _open_file() as f:

        print('Taking sensor reading with an empty bucket')
        mappings = []
        current_vol = 0
        try:
            reading = _get_distance_or_quit(sensor)
        except _NoMoreInputException:
            # Following a sensor error user wants to quit already.
            exit(0)
        print(f'New mapping: {reading}mm = 0ml.')
        mappings.append((reading, current_vol))

        last_added_vol = 0
        # Loop until user quits.
        while True:
            # Increment vol based on user input.
            print('\nAdd liquid to the bucket, wait for waves to subside.')
            try:
                last_added_vol = _get_input_vol(
                                'Enter volume of liquid added (in millimeters)',
                                last_added_vol)
            except _NoMoreInputException:
                break
            current_vol += last_added_vol

            # Read the sensor. If problem user can retry or quit.
            try:
                reading = _get_distance_or_quit(sensor)
            except _NoMoreInputException:
                break
            print(f'New mapping: {reading}mm = {current_vol}ml.')

            mappings.append((reading, current_vol))

        print('Writing mapping file.')
        # Use print to put a newline at the end of the output file.
        print(json.dumps(mappings, indent=4),file=f)
        print('Done.')


if __name__ == "__main__":
    main()
