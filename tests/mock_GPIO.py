from collections import defaultdict

# Inspired by code from Joe Sacher https://github.com/sacherjj
# Docs http://www.joesacher.com/blog/2017/10/14/rpi-hardware-mocking/

"""
Simulates a board that is interfaced via RPi.GPIO for mock test purposes.
Set and get pin direction (IN or OUT) and state (HIGH or LOW).
You can register callbacks on state transitions as part of your emulation.
"""
# Constants defined in GPIO.
# First the ones we actually use:
BCM = 11
BOARD = 10
FALLING = 32
RISING = 31
HIGH = 1
LOW = 0
IN = 1
OUT = 0
UNKNOWN = -1

# Then the ones we don't.
# Future use:
BOTH = 33
HARD_PWM = 43
I2C = 42
PUD_DOWN = 21
PUD_OFF = 20
PUD_UP = 22
SERIAL = 40
SPI = 41
VERSION = '0.7.0'  # When I developed this mock, it was against this version.

# Mapping of BOARD pin numbers (= key, the first number) to BCM pin numbers.
# Taken from the original code. Note we no longer use the mapping itself,
# only the 2 'lists' of valid pin numbers.
_board_to_bcm = {3: 2,
                 5: 3,
                 7: 4,
                 8: 14,
                 10: 15,
                 11: 17,
                 12: 18,
                 13: 27,
                 15: 22,
                 16: 23,
                 18: 24,
                 19: 10,
                 21: 9,
                 22: 25,
                 23: 11,
                 24: 8,
                 26: 7,
                 27: 0,
                 28: 1,
                 29: 5,
                 31: 6,
                 32: 12,
                 33: 13,
                 35: 19,
                 36: 16,
                 37: 26,
                 38: 20,
                 40: 21}

_valid_pins = {
    UNKNOWN: (),
    BCM: _board_to_bcm.values(),
    BOARD: _board_to_bcm.keys()
}

# BOARD or BCM
_mode = UNKNOWN

# Holds current status [ direction, state ] for each pin
# where direction is IN or OUT and state is HIGH or LOW.
_pins = {}

# Hold list of callbacks for edge transititions
# [ direction, (partial)function ], indexed by pin.
# where direction is RISING (ie LOW to HIGH) or FALLING (ie HIGH to LOW).
_edge_callback = defaultdict(list)

def _cleanup():
    # Reset the board. With apologies to the gods of DRY.
    global _mode
    global _pins
    global _edge_callback

    _mode = UNKNOWN
    _pins = {}
    _edge_callback = defaultdict(list)


def _get_board_mode():
    """Return the board's mode: BCM, BOARD or UNKNOWN if not initialised yet."""
    return _mode

def _set_board_mode(pin_numbering_style):
    """Set the board's mode: BCM or BOARD."""
    global _mode
    global _pins

    if pin_numbering_style not in (BCM, BOARD):
        raise ValueError('mode should be BCM or BOARD.')
    _mode = pin_numbering_style

    pin_list = _board_to_bcm.values() if _mode == BCM else _board_to_bcm.keys()

    # Initialise the board. You may prefer to set these to something else,
    # including UNKNOWN, depending on the behaviour of the board under
    # simuation.
    # You could then test that pins have been setup before being used.
    _pins = {}
    for pin in pin_list:
       _pins[pin] = { 'direction':IN, 'state':LOW }


def is_input(pin):
    """Test given pin's direction is set as input. Returns True / False."""
    _check_pin_number(pin)
    return _pins[pin]['direction'] == IN

def is_output(pin):
    """Test given pin's direction is set as output. Returns True / False."""
    _check_pin_number(pin)
    return _pins[pin]['direction'] == OUT

def get_direction(pin):
    """Returns direction (IN or OUT) for given pin."""
    _check_pin_number(pin)
    return _pins[pin]['direction']

def set_direction(pin, direction, clear_callbacks = True):
    """Sets direction (IN or OUT) for given pin.
    Optionally, but by default, clear any callbacks on this pin.
    This will happen even if the old direction is the same as the new."""
    _check_pin_number(pin)
    if direction not in (IN, OUT):
        raise ValueError(f'Expected {IN} or {OUT}, got {direction}')
    _pins[pin]['direction'] = direction
    if clear_callbacks:
        deregister_event_callback(pin, edge_type = None, callback = None)


def input_is_high(pin):
    _check_pin_number(pin)
    if is_input(pin):
        return _pins[pin]['state'] == HIGH
    raise ValueError(f'Pin {pin} is not set to IN direction.')

def input_is_low(pin):
    _check_pin_number(pin)
    if is_input(pin):
        return _pins[pin]['state'] == LOW
    raise ValueError(f'Pin {pin} is not set to IN direction.')

def get_input_state(pin):
    """Check pin direction is input. If so return its state (HIGH or LOW).

    Set state using simulate_input_state_change in whatever test code you
    use to simulate your GPIO board's behaviour."""
    _check_pin_number(pin)
    if is_input(pin):
        return _pins[pin]['state']
    raise ValueError(f'Pin {pin} is not set to IN direction.')

def init_input_state(pin, state):
    """Setup an IN pin's HIGH or LOW state. Only use during initialisation -
    will not trigger callbacks.
    But then should you have callbacks at that point anyway?"""
    _check_pin_number(pin)
    if not is_input(pin):
        raise ValueError(f'Pin {pin} is not set to IN direction.')
    if state not in (HIGH, LOW):
        raise ValueError(f'Expected {HIGH} or {LOW}, got {state}')
    _pins[pin]['state'] = state

def simulate_input_state_change(pin, state):
    """Simulate an IN pin getting set by the GPIO board.

    If this changes the state,
        execute any callbacks registered for that transition.
    else:
        return silently.

    If that 'silently' is a problem ie you expect your code to always change
    the state, never to set it to the same state it already is,
    then do a get_input_state test before calling this function.
    """
    _check_pin_number(pin)
    if not is_input(pin):
        raise ValueError(f'Pin {pin} is not set to IN direction.')
    _state_change(pin, IN, state)


def output_is_high(pin):
    _check_pin_number(pin)
    if is_output(pin):
        return _pins[pin]['state'] == HIGH
    raise ValueError(f'Pin {pin} is not set to OUT direction.')

def output_is_low(pin):
    _check_pin_number(pin)
    if is_output(pin):
        return _pins[pin]['state'] == LOW
    raise ValueError(f'Pin {pin} is not set to OUT direction.')

def get_output_pin_state(pin):
    """Test that an OUT pin has been set correctly."""
    _check_pin_number(pin)
    if is_output(pin):
        return _pins[pin]['state']
    raise ValueError(f'Pin {pin} is not set to OUT direction.')

def init_output_state(pin, state):
    """Setup an OUT pin to HIGH or LOW. Only use during initialisation -
    will not trigger callbacks.
    But then should you have callbacks at that point anyway?"""
    _check_pin_number(pin)
    if not is_output(pin):
        raise ValueError(f'Pin {pin} is not set to OUT direction.')
    if state not in (HIGH, LOW):
        raise ValueError(f'Expected {HIGH} or {LOW}, got {state}')
    _pins[pin]['state'] = state

def set_output_pin_state(pin, state):
    """Set an output pin to state, HIGH or LOW.

    If this changes the state:
        execute any callbacks registered for that transition.
    else:
        return silently.

    If that 'silently' is a problem ie you expect your code to always change
    the state, never to set it to the same state it already is,
    then do a get_output_state test before calling this function.
    """
    _check_pin_number(pin)
    if not is_output(pin):
        raise ValueError(f'Pin {pin} is not set to OUT direction.')
    _state_change(pin, OUT, state)


def _state_change(pin, direction, state):
    global _pins

    if state not in (HIGH, LOW):
        raise ValueError(f'Expected {HIGH} or {LOW}, got {state}')
    if state == _pins[pin]['state']:
        return

    _pins[pin]['state'] = state
    _trigger_any_edge_callbacks(pin, RISING if state == HIGH else FALLING)

def _trigger_any_edge_callbacks(pin, edge_type):
    for callpair in _edge_callback[pin]:
        if callpair[0] == edge_type:
            callpair[1]()

def register_event_callback(pin, edge_type, callback):
    global _edge_callback

    _check_pin_number(pin)
    if edge_type not in (RISING, FALLING):
        raise ValueError('Edge_type should be RISING or FALLING.')
    _edge_callback[pin].append((edge_type, callback))

def deregister_event_callback(pin, edge_type = None, callback = None):
    global _edge_callback

    _check_pin_number(pin)
    if edge_type not in (RISING, FALLING, None):
        raise ValueError('Edge_type should be RISING or FALLING (or None).')
    for callpair in _edge_callback[pin]:
        if edge_type == None or callpair[0] == edge_type:
            if callback == None or callpair[1] == callback:
                _edge_callback[pin].remove(callpair)
                # No return - could be multiple callbacks on that condistion.


# Handle the fact that the different board types have different numbering
# schemes.
def _check_pin_number(pin):
    if _mode == UNKNOWN:
        raise ValueError('Mode has not been set.')
    if pin not in _valid_pins[_mode]:
        raise ValueError(f'Pin_number {pin} is invalid for mode: {_mode}')


# Could also add some tests to verify that you are not trying to set
# a volatge pin, etc?
def get_registered_event_callbacks():
    raise NotImplementedError

# GPIO library functions
def add_event_callback():
    raise NotImplementedError

def add_event_detect():
    raise NotImplementedError

def event_detected():
    raise NotImplementedError

def gpio_function():
    raise NotImplementedError

def remove_event_detect():
    raise NotImplementedError

def setwarnings():
    raise NotImplementedError

def wait_for_edge():
    raise NotImplementedError
# Also not implemented: anything to do with PWM, I2C, SPI.

# Map all implemented GPIO function names to our internal naming scheme.
def getmode():
    return _get_board_mode()

def setmode(pin_numbering_style):
    return _set_board_mode(pin_numbering_style)

def setup(pin, direction):
    # Always clear callbacks when setting pin direction. Your Mileage May Vary.
    return set_direction(pin, direction, clear_callbacks = True)

def output(pin, state):
    return set_output_pin_state(pin, state)

def input(pin):
    return get_input_state(pin)

def cleanup():
    return _cleanup()
