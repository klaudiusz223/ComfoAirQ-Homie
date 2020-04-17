import time

from .homie_device.device_comfoairq_gateway import  Device_ComfoAirQ_Gateway
from .homie_device.device_comfoairq         import  Device_ComfoAirQ


class ComfoAirQ_Homie(object):

    devices = []
    device_comfo = None

    def __init__(self,
                device_id=None,
                name=None,
                homie_settings=None, 
                mqtt_settings=None,  
                sensors_definition = None,
                comfoconnect_settings=None
    ):
        assert device_id
        assert name
        assert mqtt_settings
        assert comfoconnect_settings
        
        self.device_id=device_id
        self.name=name
        self.mqtt_settings = mqtt_settings


        self.devices.append(None)

        self.device_gateway = Device_ComfoAirQ_Gateway(device_id=self.device_id + "gateway",name=self.name + "Gateway",
                                                        homie_settings=homie_settings,mqtt_settings=self.mqtt_settings,
                                                        connect_at_start = comfoconnect_settings['COMFOCONNECT_AUTOCONNECT'],
                                                        device_comfoairq=
                                                        Device_ComfoAirQ(device_id=self.device_id, name=self.name,
                                                                        homie_settings=homie_settings,mqtt_settings=self.mqtt_settings,
                                                                        comfoconnect_settings=comfoconnect_settings
                                                                        )
                                                        )

        


    def exit(self):
        # self.device_comofo.exit()
        # self.device_gateway.state = 'disconnected'
        self.device_gateway.exit()
        

