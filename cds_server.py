import os
import time
import json
import shutil
import threading
# import cv2
import io
import numpy as np
from flask import Flask
from flask import render_template, request, redirect, url_for, send_file
from flask_socketio import SocketIO, send, emit

import memcache
mc = memcache.Client(['127.0.0.1:12000'], debug=True)

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/lunatic", methods=["GET"])
def lunatic():
    return render_template("lunatic.html")


@socketio.on('connect', namespace='/remiria')
def remiria_connect():
    print('remiria scarlet has been connected')


@socketio.on('change_ip', namespace='/remiria')
def change_current_ip(data):
    mc.set("current_ip", data.get('param'))


@app.route('/upload', methods=['POST'])
def set_base64():
    # current_ip = (request.args.get('address') or "0.0.0.0")
    image_data = request.get_data() or "None"

    socketio.emit('frame_data', {'data': image_data}, namespace='/remiria')

    # global stream_ip
    # if current_ip[1] == '1':
    #     stream_ip = current_ip[0]

    # if current_ip[0] == stream_ip:
    #     socketio.emit('frame_data', {'data': image_data}, namespace='/remiria')

    return "Done"


# def loop_fun(latency=0.01):
#     while True:
#         image_data = mc.get('frame') or "None"
#         socketio.emit('frame_data', {'data': image_data}, namespace='/remiria')
#         time.sleep(latency)


# @app.route('/download', methods=['GET'])
# def get_base64():
#     camera_ip = request.args.get('camera') or "0.0.0.0"
#     # nparr = np.fromstring(image_data, np.uint8)
#     nparr = np.fromstring(image_data_dict.get(camera_ip, "None"), np.uint8)

#     return send_file(io.BytesIO(nparr), mimetype='image/jpeg')


if __name__ == "__main__":
    # threading.Thread(
    #     target=lambda: loop_fun(0.03)
    # ).start()
    socketio.run(app, debug=True, port=6789, host='0.0.0.0')
