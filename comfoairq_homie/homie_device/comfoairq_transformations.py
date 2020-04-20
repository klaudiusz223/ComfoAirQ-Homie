import datetime
import struct

import logging

logger = logging.getLogger(__name__)

def multiply(var,value,function_args):
    return round(value * function_args[0],1)


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
