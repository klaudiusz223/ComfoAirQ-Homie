import datetime
import struct

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


import numpy
from numpy_ringbuffer import RingBuffer


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError( "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=numpy.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y



fan_speed_buffers = {}

def transform_smooth_fan_speed(var,value,function_args):
    # print(function_args[0])
    buffer_name = function_args[0]
    window_length = function_args[1]
    window =  function_args[2]


    if not buffer_name in fan_speed_buffers.keys():
        fan_speed_buffers[buffer_name] = RingBuffer(capacity=window_length, dtype=numpy.integer)
    fan_speed_buffers[buffer_name].append(value)
    # print(fan_speed_buffers[buffer_name])

    smoothed = smooth(numpy.array(fan_speed_buffers[buffer_name]),window_len=len(fan_speed_buffers[buffer_name]),window=window)

    # print(smoothed)

    # print(smoothed[-1])
    # print(int(round(smoothed[-1])))

    # print("RB {}".format(len(fan_speed_buffers[buffer_name])))
    # print(len(smoothed))
    return int(round(smoothed[-1]))    
    # return value