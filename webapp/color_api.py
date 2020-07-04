#!/usr/bin/python3

import flask, logging, time, argparse, threading
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


LED_threads = []
break_out_of_current_thread = False


class ThreadRunner(threading.Thread):
    def __init__(self, threadID, name, func):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.func = func
        logger.info("Created thread with ThreadID=" + str(threadID) + " and name=" + self.name + ".")

    def run(self):
        logger.info("Starting " + self.name)
        self.func()
        logger.info("Exiting " + self.name)


@app.route('/', methods=['GET'])
def home():
    logger.info("ColorApi: Change the color of a string of ws2811 LEDs on a raspi with google assistant.") 
    return '''<h1>ColorApi</h1><p>Change the color of a string of ws2811 LEDs on a raspi with google assistant.</p>''' + "\n"


@app.route('/pilight/color/<command>', methods=['GET'])
def color_api(command):
    global break_out_of_current_thread
    break_out_of_current_thread = True
    logger.info("A function request was made using the Color API. The keyword used in the request was \"" + str(command) + "\"") 
    decide_function(command)
    return '''<h1>ColorApi</h1><p>A function request was made using the Color API. 
    The keyword used in the request was \"{command}\".</p>'''.format(command=command) + "\n"


@app.route('/pilight/brightness/<brightness>', methods=['GET'])
def color_api_brightness(brightness):
    logger.info("A brightness request was made using the Color API. The keyword used in the request was \"" + str(brightness) + "\"") 
    change_brightness(brightness)
    return '''<h1>ColorApi</h1><p>A brightness request was made using the Color API. 
    The value in the request was \"{brightness}\".</p>'''.format(brightness=brightness) + "\n"


@app.errorhandler(404)
def page_not_found(e):
    logger.error("404: The resource could not be found.") 
    return "<h1>404</h1><p>The resource could not be found.</p>\n", 404


def start_new_thread(func, name):
    while check_for_running_threads():
        time.sleep(0.005)
    new_thread = ThreadRunner(1, name, func)
    start_thread(new_thread)
    LED_threads.append(new_thread)


def start_thread(func_thread):
    thread = func_thread
    thread.start()


def check_for_running_threads():
    global LED_threads
    running_threads = [thread for thread in LED_threads if thread.isAlive()]
    LED_threads = running_threads
    return True if len(LED_threads) > 0 else False


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    logger.debug("running the " + colorWipe.__name__ + " function.")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    logger.debug("running the " + theaterChase.__name__ + " function.")
    for j in range(iterations):
        if not break_out_of_current_thread:
            for q in range(3):
                if not break_out_of_current_thread:
                    for i in range(0, strip.numPixels(), 3):
                        strip.setPixelColor(i+q, color)
                    strip.show()
                    time.sleep(wait_ms/1000.0)
                    for i in range(0, strip.numPixels(), 3):
                        strip.setPixelColor(i+q, 0)
                else:
                    break
        else:
            break


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    logger.debug("running the " + wheel.__name__ + " function.")
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
    logger.debug("running the " + rainbow.__name__ + " function.")
    for j in range(256*iterations):
        if not break_out_of_current_thread:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i+j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
        else:
            break


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    logger.debug("running the " + rainbowCycle.__name__ + " function.")
    for j in range(256*iterations):
        if not break_out_of_current_thread:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
        else:
            break


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    logger.debug("running the " + theaterChaseRainbow.__name__ + " function.")
    for j in range(256):
        if not break_out_of_current_thread:
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, wheel((i+j) % 255))
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)
        else:
            break


def solid_color(r, g, b):
    """Solid color across display a pixel at a time."""
    logger.debug("running the " + solid_color.__name__ + " function.")
    r = r*LED_BRIGHTNESS
    g = g*LED_BRIGHTNESS
    b = b*LED_BRIGHTNESS
    colorWipe(strip, Color(g, r, b))


def clear(ms_btwn_bulbs):
    logger.debug("running the " + solid_color.__name__ + " function with ms_btwn_bulbs var = " 
        + str(ms_btwn_bulbs) + ".")
    colorWipe(strip, Color(0,0,0), ms_btwn_bulbs)


def turn_off():
    logger.debug("running the " + turn_off.__name__ + " function.")
    solid_color(0, 0, 0)


def turn_on():
    logger.debug("running the " + turn_on.__name__ + " function.")
    solid_color(1, 1, 1)


def turn_red():
    logger.debug("running the " + turn_red.__name__ + " function.")
    solid_color(1, 0, 0)


def turn_blue():
    logger.debug("running the " + turn_blue.__name__ + " function.")
    solid_color(0, 0, 1)


def turn_green():
    logger.debug("running the " + turn_green.__name__ + " function.")
    solid_color(0, 1, 0)


def turn_cyan():
    logger.debug("running the " + turn_cyan.__name__ + " function.")
    solid_color(0, 1, 1)


def turn_magenta():
    logger.debug("running the " + turn_magenta.__name__ + " function.")
    solid_color(1, 0, 1)


def turn_yellow():
    logger.debug("running the " + turn_yellow.__name__ + " function.")
    solid_color(1, 1, 0)


def do_rainbow():
    logger.debug("running the " + do_rainbow.__name__ + " function.")
    while not break_out_of_current_thread:
        rainbow(strip)


def do_rainbow_chase():
    logger.debug("running the " + do_rainbow_chase.__name__ + " function.")
    while not break_out_of_current_thread:
        theaterChaseRainbow(strip)


def do_strobe():
    logger.debug("running the " + do_strobe.__name__ + " function.")
    while not break_out_of_current_thread:
        theaterChase(strip, Color(255, 255, 255))


def do_combo():
    logger.debug("running the " + do_combo.__name__ + " function.")
    while not break_out_of_current_thread:
        colorwipe_cycle()
        rainbow(strip, 20, 2)
        rainbow_cycle()


def do_colorwipe_cycle():
    logger.debug("running the " + do_colorwipe_cycle.__name__ + " function.")
    while not break_out_of_current_thread:
        colorwipe_cycle()


def colorwipe_cycle():
    func_list = [turn_blue, turn_red, turn_magenta, turn_green, turn_cyan, turn_yellow, turn_on, turn_off]
    for func in func_list:
        if not break_out_of_current_thread:
            func()
        else:
            break


def do_rainbow_cycle():
    logger.debug("running the " + do_rainbow_cycle.__name__ + " function.")
    while not break_out_of_current_thread:
        rainbow_cycle()


def rainbow_cycle():
    rainbowCycle(strip, 20)


def change_brightness(brightness):
    logger.debug("running the " + change_brightness.__name__ + " function.")
    pass


def decide_function(command):
    global break_out_of_current_thread
    logger.debug("running the " + decide_function.__name__ + " function.")
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
        "strobe"        : do_strobe,
        "combo"         : do_combo,
        "rainbow"       : do_rainbow,
        "rainbow cycle" : do_rainbow_cycle,
        "rainbow chase" : do_rainbow_chase,
        "color flip"    : do_colorwipe_cycle
    }
    function = command_dict.get(command.lower(), None)
    if function:
        clear(20)
        break_out_of_current_thread = False
        start_new_thread(function(), function.__name__)
    else:
        logger.error("The command\"" + command + "\" could not be found.") 


if __name__ == '__main__':
    # Process arguments
    logger.debug("running the " + __name__ + " function.")
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