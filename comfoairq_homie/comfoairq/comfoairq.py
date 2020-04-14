import time
from pycomfoconnect import *

class ComfoAirQ(object):


    comfoconnect_settings = {}
    comfoconnect_bridge = None
    comfoconnect = None
    callback_sensor = None
    connection_event : threading.Event = None
    registered_sensors = {}
    _stay_connected = False
    _exit = False

    state_callbacks = []


    def __init__(self, comfoconnect_settings = None):

        assert comfoconnect_settings

        self.comfoconnect_settings = comfoconnect_settings
        self.connection_event = threading.Event()

        self._init_thread = threading.Thread(target=self._init_thread_loop,name="ComfoAirQInitThread")
        self._init_thread.start()




    def bridge_discovery(self,host = None):
        ## Bridge discovery ################################################################################################

        # Method 1: Use discovery to initialise Bridge
        # bridges = Bridge.discover(timeout=1)
        # if bridges:
        #     bridge = bridges[0]
        # else:
        #     bridge = None

        # Method 2: Use direct discovery to initialise Bridge
        bridges = Bridge.discover(host)
        if bridges:
            bridge = bridges[0]
        else:
            bridge = None

        # Method 3: Setup bridge manually
        # bridge = Bridge(args.ip, bytes.fromhex('0000000000251010800170b3d54264b4'))

        if bridge is None:
            print("No bridges found!")
            return None

        print("Bridge found: %s (%s)" % (bridge.uuid.hex(), bridge.host))

        bridge.debug = False

        return bridge
    
    def callback_sensor_function(self,var,value):
        if self.callback_sensor is not None:
            self.callback_sensor(var,value)

    def register_sensor(self, sensor_id, sensor_type = None):
        self.registered_sensors[sensor_id] = sensor_type
        if self.comfoconnect:
            if self.comfoconnect.is_connected():
                self.comfoconnect.register_sensor(sensor_id,sensor_type)


    def exit(self):
        self._exit = True
        self.connection_event.set()
        pass
    
    def disconnect(self):
        if self.comfoconnect.is_connected():
            self.comfoconnect.disconnect()
        self.run_on_state_change_callbacks()

    def connect(self):
        if not self.comfoconnect.is_connected():
            self.comfoconnect.connect()
            for sensor in self.registered_sensors:
                self.comfoconnect.register_sensor(sensor,self.registered_sensors[sensor])
        self.run_on_state_change_callbacks()


    def _comfoconnect_thread_loop(self):
        while not self._exit:
            event_recieved = self.connection_event.wait(60)
            if event_recieved:
                self.connection_event.clear()
                if self._exit:
                    break
                if self._stay_connected:
                    self.connect()
                elif not self._stay_connected:
                    self.disconnect()
            else:
                self.run_on_state_change_callbacks()
        self.disconnect()

    def _init_thread_loop(self):
        while not self._exit:
            self.comfoconnect_bridge = self.bridge_discovery(self.comfoconnect_settings['COMFOCONNECT_HOST'])

        ## Setup a Comfoconnect session  ###################################################################################
            if  self.comfoconnect_bridge is not None:
                self.comfoconnect = ComfoConnect(self.comfoconnect_bridge, 
                                                bytes.fromhex(self.comfoconnect_settings['COMFOCONNECT_UUID']), 
                                                self.comfoconnect_settings['COMFOCONNECT_NAME'],
                                                self.comfoconnect_settings['COMFOCONNECT_PIN'])
                self.comfoconnect.callback_sensor = self.callback_sensor_function

                self._comfoconnect_thread = threading.Thread(target=self._comfoconnect_thread_loop,name="ComfoAirQThread")
                self._comfoconnect_thread.start()

                if self.comfoconnect_settings['COMFOCONNECT_AUTOCONNECT']:
                    self._stay_connected = True
                    self.connection_event.set()
                break
        # time.sleep(60)

    def add_on_state_change_callback(self, callback):
        self.state_callbacks.append(callback)

    def run_on_state_change_callbacks(self):
        for callback in self.state_callbacks:
            try:
                callback()
            except Exception as e:
                pass