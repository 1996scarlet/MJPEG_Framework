# -*- coding: utf-8 -*-
from interface import HKIPCamera
import cv2
import sys
import time
import copy
import argparse
import threading

from termcolor import colored
import requests

import memcache
mc = memcache.Client(['127.0.0.1:12000'], debug=True)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('ip_address', type=str,
                        help='IP address of web camera.')

    return parser.parse_args(argv)


# =================== ARGS ====================
args = parse_arguments(sys.argv[1:])

ip_address = args.ip_address

# =================== CAMERA INIT ====================

hkcp = HKIPCamera(b"10.41.0.231", 8000, b"admin", b"humanmotion01")
hkcp.start()

print(colored('=>_<= Loading the first frame ... =>_<=', 'red'))
time.sleep(1)

while True:
    time.sleep(0.02)
    if mc.get("current_ip") == ip_address:
        try:
            requests.post("http://127.0.0.1:6789/upload",
                          data=cv2.imencode('.jpg', hkcp.frame())[1].tostring())
        except:
            print(
                colored('=>_<= Do not forget to start cds flask server =>_<=', 'yellow'))

hkcp.stop()
