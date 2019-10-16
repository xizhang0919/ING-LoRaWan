from __future__ import absolute_import

import ttn
import os
from flask import Flask, render_template
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


class Status():
    def __init__(self):
        self.status = 'default'

    def update_status(self, update):
        self.status = update

    def get_status(self):
        return str(self.status)


status = Status()


# message receiving callback
def uplink_callback(msg, client):
    base64_decoded_message = base64.b64decode(msg.payload_raw)
    raw_message = base64_decoded_message.decode()
    # update status
    status.update_status(raw_message)

    # temp = str(raw_message)
    print('Getting messages from application {} with payload {} {}'
          .format(msg.dev_id, raw_message, status.get_status()))


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
    return '"high"'


if __name__ == '__main__':
    app.run(host='localhost', port=8888)
