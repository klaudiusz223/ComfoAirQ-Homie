import datetime
import struct
import time

import logging

logger = logging.getLogger(__name__)

def multiply(var,value,function_args):
    return round(value * function_args[0],function_args[1])


def calculate_end_date(var,value,function_args):
    if value == 'ffffffff':
        secs = 0
    else:
        secs = struct.unpack('<i', bytes.fromhex(value))[0]
    return (datetime.datetime.now() + datetime.timedelta(0,secs)).strftime('%Y-%m-%dT%H:%M:%S.0')

def calculate_timer(var,value,function_args):
    if value == 'ffffffff':
        secs = 0
    else:
        secs = struct.unpack('<i', bytes.fromhex(value))[0]
    return secs


def transform_dict(var,value,function_args):
    return function_args[value]

slow_down_dict = {}

def slow_down(var,value,function_args):
    # print(function_args[0])
    sensor_name = function_args[0]
    timeout = function_args[1]
    treshold =  function_args[2]
    if not sensor_name in slow_down_dict.keys() or abs((value - slow_down_dict[sensor_name][0])) > abs(treshold  * value) or time.time() >= (slow_down_dict[sensor_name][1] + timeout ):
        slow_down_dict[sensor_name] = (value,time.time())
        return value
    else:
        return None
