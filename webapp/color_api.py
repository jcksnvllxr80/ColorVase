#!/usr/bin/python3

import flask, loggingn, time, argparse
from flask import request, jsonify
from rpi_ws281x import *


'''   ############ USAGE ###############
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
'''
logger = logging.getLogger(__name__)   
logger.setLevel(logging.DEBUG)
logger.propagate = False
# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [color_api.py] [%(levelname)-5.5s]  %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# LED strip configuration:
LED_COUNT      = 25      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


@app.route('/', methods=['GET'])
def home():
    logger.info("ColorApi: Change the color of a string of ws2811 LEDs on a raspi with google assistant.") 
    return '''<h1>ColorApi</h1><p>Change the color of a string of ws2811 LEDs on a raspi with google assistant.</p>''' + "\n"


@app.route('/pilight/color/<command>', methods=['GET'])
def api_all(command):
    logger.info("A request was made using the color API. The keyword used in the request was \"" + str(color) + "\"") 
    return '''<h1>ColorApi</h1><p>A request was made using the color API. 
    The keyword used in the request was \"{command}\".</p>'''.format(command=command) + "\n"
    decide_color_function(command)


@app.errorhandler(404)
def page_not_found(e):
    logger.error("404: The resource could not be found.") 
    return "<h1>404</h1><p>The resource could not be found.</p>\n", 404


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def solid_color(r, g, b):
    """Solid color across display a pixel at a time."""
    r = r*LED_BRIGHTNESS
    g = g*LED_BRIGHTNESS
    b = b*LED_BRIGHTNESS
    colorWipe(strip, Color(r, g, b))


def clear(ms_btwn_bulbs):
    colorWipe(strip, Color(0,0,0), ms_btwn_bulbs)


def turn_off():
    solid_color(0, 0, 0)


def turn_on():
    solid_color(1, 1, 1)


def turn_red():
    solid_color(1, 0, 0)


def turn_blue():
    solid_color(0, 0, 1)


def turn_green():
    solid_color(0, 1, 0)


def turn_cyan():
    solid_color(0, 1, 1)


def turn_magenta():
    solid_color(1, 0, 1)


def turn_yellow():
    solid_color(1, 1, 0)


def do_rainbow():
    pass


def do_chase():
    pass


def do_rainbow_chase():
    pass


def do_strobe():
    pass


def do_wheel():
    pass


def decide_color_function(command):
    command_dict = {
        "off"           : turn_off,
        "on"            : turn_on,
        "red"           : turn_red,
        "blue"          : turn_blue,
        "green"         : turn_green,
        "cyan"          : turn_cyan,
        "magenta"       : turn_magenta,
        "yellow"        : turn_yellow,
        "white"         : turn_on,
        "rainbow"       : do_rainbow,
        "chase"         : do_chase,
        "strobe"        : do_strobe,
        "wheel"         : do_wheel,
        "rainbow chase" : do_rainbow_chase
    }

    function = command_dict.get(command.lower(), None)
    if function:
        clear(20)
        function()
    else:
        logger.error("The command\"" + command + "\" could not be found.") 


# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest='port', nargs='?', help='port to connect on')
parser.add_argument('-b', '--brightness', dest='brightness', nargs='?', help='brightness of bulbs')
args = parser.parse_args()
if args.port:
    port = args.port
else:
    port = 5000
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()
app.run(host='0.0.0.0', port=port)