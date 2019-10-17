from __future__ import absolute_import

import ttn
import os
from flask import Flask, render_template, jsonify
import base64

# set env variable
os.environ["FLASK_ENV"] = "development"

# create Flask app
app = Flask(__name__)

# TTN application id and key
app_id = "lorawan-ing"
access_key = "ttn-account-v2.aRjE5PGhlD_4ipcULYAFvFl_GTKLHQSkKiZjaq6SNxQ"

# decoder function
decoder_fn = """function Decoder(payload) {return { raw_data: String.fromCharCode.apply(null, payload) };}"""

moisture_types = {'L': 'low', 'M': 'medium', 'H':'high'}

class Status():
    def __init__(self):
        self.moisture = 'L'
        self.temperature = '24.20'

    def update_status(self, updated_moisture, updated_temperature):
        self.moisture = updated_moisture
        self.temperature = updated_temperature
    
    def get_status(self):
        return moisture_types[moisture], temperature


STATUS = Status()

def get_moisture(raw_message):
    return raw_message.split('#')[0]

def decode_num(num_str):
    num = str()
    for i in num_str:
        val = ord(i) - 65
        num += str(val)
    return num

def get_temperature(raw_message):
    parts = a.split('#')
    base_num = decode_num(parts[1])
    decimal_point = decode_num(parts[2])
    return '{}.{}'.format(base_num, decimal_point)

# message receiving callback
def uplink_callback(msg, client):
    base64_decoded_message = base64.b64decode(msg.payload_raw)
    raw_message = base64_decoded_message.decode()
    moisture = get_moisture(raw_message)
    temperature = get_temperature(raw_message)
    # update status
    STATUS.update_status(moisture, temperature)

    # temp = str(raw_message)
    print('Getting messages from application {} with payload {} moisture {} temperature {}'
          .format(msg.dev_id, raw_message, moisture, temperature))


# create ttn handler
lorawan_handler = ttn.HandlerClient(app_id, access_key)


# create application client
app_client = lorawan_handler.application()
app_client.set_custom_payload_functions(decoder=decoder_fn)


# create mqtt client
mqtt_client = lorawan_handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    moisture_latest, temperature_latest = STATUS.get_status()
    return jsonify(
        mositure=moisture_latest,
        temperature=temperature_latest
    )


if __name__ == '__main__':
    app.run(host='localhost', port=8888)
