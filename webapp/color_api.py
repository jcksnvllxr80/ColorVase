#!/usr/bin/python3

import flask, logging, time, argparse
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
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
new_command = False


@app.route('/', methods=['GET'])
def home():
    logger.info("ColorApi: Change the color of a string of ws2811 LEDs on a raspi with google assistant.") 
    return '''<h1>ColorApi</h1><p>Change the color of a string of ws2811 LEDs on a raspi with google assistant.</p>''' + "\n"


@app.route('/pilight/color/<command>', methods=['GET'])
def api_all(command):
    new_command = True
    logger.info("A request was made using the color API. The keyword used in the request was \"" + str(command) + "\"") 
    decide_color_function(command)
    return '''<h1>ColorApi</h1><p>A request was made using the color API. 
    The keyword used in the request was \"{command}\".</p>'''.format(command=command) + "\n"


@app.errorhandler(404)
def page_not_found(e):
    logger.error("404: The resource could not be found.") 
    return "<h1>404</h1><p>The resource could not be found.</p>\n", 404


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    logger.info("running the " + colorWipe.__name__ + " function.")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    logger.info("running the " + theaterChase.__name__ + " function.")
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
    logger.info("running the " + wheel.__name__ + " function.")
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
    logger.info("running the " + rainbow.__name__ + " function.")
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    logger.info("running the " + rainbowCycle.__name__ + " function.")
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    logger.info("running the " + theaterChaseRainbow.__name__ + " function.")
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
    logger.info("running the " + solid_color.__name__ + " function.")
    r = r*LED_BRIGHTNESS
    g = g*LED_BRIGHTNESS
    b = b*LED_BRIGHTNESS
    colorWipe(strip, Color(g, r, b))


def clear(ms_btwn_bulbs):
    logger.info("running the " + solid_color.__name__ + " function with ms_btwn_bulbs var = " 
        + str(ms_btwn_bulbs) + ".")
    colorWipe(strip, Color(0,0,0), ms_btwn_bulbs)


def turn_off():
    logger.info("running the " + turn_off.__name__ + " function.")
    solid_color(0, 0, 0)


def turn_on():
    logger.info("running the " + turn_on.__name__ + " function.")
    solid_color(1, 1, 1)


def turn_red():
    logger.info("running the " + turn_red.__name__ + " function.")
    solid_color(1, 0, 0)


def turn_blue():
    logger.info("running the " + turn_blue.__name__ + " function.")
    solid_color(0, 0, 1)


def turn_green():
    logger.info("running the " + turn_green.__name__ + " function.")
    solid_color(0, 1, 0)


def turn_cyan():
    logger.info("running the " + turn_cyan.__name__ + " function.")
    solid_color(0, 1, 1)


def turn_magenta():
    logger.info("running the " + turn_magenta.__name__ + " function.")
    solid_color(1, 0, 1)


def turn_yellow():
    logger.info("running the " + turn_yellow.__name__ + " function.")
    solid_color(1, 1, 0)


def do_rainbow():
    logger.info("running the " + do_rainbow.__name__ + " function.")
    pass


def do_chase():
    logger.info("running the " + do_chase.__name__ + " function.")
    pass


def do_rainbow_chase():
    logger.info("running the " + do_rainbow_chase.__name__ + " function.")
    pass


def do_strobe():
    logger.info("running the " + do_strobe.__name__ + " function.")
    pass


def do_wheel():
    logger.info("running the " + do_wheel.__name__ + " function.")
    pass


def do_colorwipe_cycle():
    logger.info("running the " + do_colorwipe_cycle.__name__ + " function.")
    while not new_command:
        turn_red()
        turn_blue()
        turn_green()
        turn_cyan()
        turn_magenta()
        turn_yellow()
        turn_on()
        turn_off()


def decide_color_function(command):
    logger.info("running the " + decide_color_function.__name__ + " function.")
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
        "rainbow chase" : do_rainbow_chase,
        "color wipe"    : do_colorwipe_cycle
    }
    function = command_dict.get(command.lower(), None)
    if function:
        clear(20)
        new_command = False
        function()
    else:
        logger.error("The command\"" + command + "\" could not be found.") 


if __name__ == '__main__':
    # Process arguments
    logger.info("running the " + __name__ + " function.")
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    logger.info("Starting the ws2811 LEDs.")
    strip.begin()
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', dest='port', nargs='?', help='port to connect on')
    parser.add_argument('-b', '--brightness', dest='brightness', nargs='?', help='brightness of bulbs')
    args = parser.parse_args()
    if args.port:
        port = args.port
    else:
        port = 5000
    app.run(host='0.0.0.0', port=port)