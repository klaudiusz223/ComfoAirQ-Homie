import time

from homie.support.repeating_timer import Repeating_Timer
from homie.device_base import Device_Base
from homie.node.node_base import Node_Base

from homie.node.property.property_switch import Property_Switch
from homie.node.property.property_enum import Property_Enum

import logging

logger = logging.getLogger(__name__)

DEVICE_STATES = ['DISCONNECTED','READY','SLEEPING','ERROR','PROBLEM']


repeating_timer = None

class Device_ComfoAirQ_Gateway(Device_Base):
    def __init__(
                self, 
                device_id=None, 
                name=None, 
                homie_settings=None, 
                mqtt_settings=None,
                device_comfoairq=None,
                connect_at_start=True,

    ):
        assert device_id
        assert name
        assert device_comfoairq
        assert mqtt_settings
        super().__init__ (device_id, name, homie_settings, mqtt_settings)

        self.device_comfoairq=device_comfoairq
# Gateway Controls
        node = Node_Base(self,'controls','ComfoAirQ Gateway Controls','controls')
        self.add_node (node)

        node.add_property(Property_Switch(node,id='stayconnected',name = 'Stay connected to Comfoconnect' ,settable = True, set_value=self.set_stay_connected))

        node.add_property(Property_Switch(node,id='reload',name = 'Publish Homie Devices' ,settable = True, set_value=self.set_reload))

        node = Node_Base(self,'sensors','ComfoAirQ Gateway Sensors','sensors')
        self.add_node (node)



        node.add_property (Property_Enum (node,id='state',name = 'Connection state',settable = False,data_format=','.join(DEVICE_STATES)))

        if self.device_comfoairq is not None:
            self.device_comfoairq.comfoairq.add_on_state_change_callback(self.publish_connection_status)
        
        global repeating_timer
        if repeating_timer == None:
            repeating_timer = Repeating_Timer(
                self.homie_settings["update_interval"]
            )

        repeating_timer.add_callback(self.publish_connection_status)

        self.start()
        if connect_at_start:
            self.set_stay_connected("ON")

        self.publish_connection_status()

    def set_stay_connected(self,value):
        if self.device_comfoairq:
            if value == "ON":
                self.device_comfoairq.connect()
            elif value == "OFF":
                self.device_comfoairq.disconnect()
            pass
            time.sleep(2)
            self.publish_connection_status()

    def set_reload(self,value):
        # OpenHAB  problems workaroud 
        # https://github.com/openhab/openhab-addons/issues/6975        
        self.publish_attributes()
        self.publish_nodes()

        if self.device_comfoairq:
            if value == "ON":
                self.device_comfoairq.publish_attributes()
                self.device_comfoairq.disconnect()
                time.sleep(1)
                self.device_comfoairq.connect()
                self.device_comfoairq.publish_nodes()                
        time.sleep(1)
        self.get_node('controls').get_property('reload').value = 'OFF'


    def publish_connection_status(self):
        if self.device_comfoairq.comfoairq is None:
            self.get_node('sensors').get_property('state').value = 'ERROR'
        elif self.device_comfoairq.comfoairq._exit:
            self.get_node('sensors').get_property('state').value = 'DISCONNECTED'
        elif self.device_comfoairq.comfoairq._stay_connected == False:
            self.get_node('sensors').get_property('state').value = 'SLEEPING'
        elif self.device_comfoairq.comfoairq.comfoconnect_bridge is None:
            self.get_node('sensors').get_property('state').value = 'ERROR'
        elif self.device_comfoairq.comfoairq.comfoconnect.is_connected() == False:
            self.get_node('sensors').get_property('state').value = 'PROBLEM'
        else:
            self.get_node('sensors').get_property('state').value = 'READY'

        if self.device_comfoairq.comfoairq._stay_connected:
            self.get_node('controls').get_property('stayconnected').value = 'ON'
        else:
            self.get_node('controls').get_property('stayconnected').value = 'OFF'

    def exit(self):
        self.state = 'disconnected'
        self.device_comfoairq.exit()