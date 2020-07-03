#!/usr/bin/python3

import flask, logging
from flask import request, jsonify


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


@app.route('/', methods=['GET'])
def home():
    logger.info("ColorApi: Change the color of a string of ws2811 LEDs on a raspi with google assistant.") 
    return '''<h1>ColorApi</h1><p>Change the color of a string of ws2811 LEDs on a raspi with google assistant.</p>''' + "\n"


@app.route('/pilight/<color>', methods=['GET'])
def api_all(color):
    logger.info("A request was made using the color API. The keyword used in the request was \"" + str(color) + "\"") 
    return '''<h1>ColorApi</h1><p>A request was made using the color API. 
    The keyword used in the request was \"{color}\".</p>'''.format(color=color) + "\n"


@app.errorhandler(404)
def page_not_found(e):
    logger.error("404: The resource could not be found.") 
    return "<h1>404</h1><p>The resource could not be found.</p>\n", 404


app.run(host='0.0.0.0', port=12345)