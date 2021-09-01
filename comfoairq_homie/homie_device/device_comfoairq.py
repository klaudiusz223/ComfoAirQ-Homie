import time
import sys
import os

from pycomfoconnect.const import *

from homie.support.repeating_timer import Repeating_Timer
from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.property.property_switch import Property_Switch
from homie.node.property.property_temperature import Property_Temperature
from homie.node.property.property_humidity import Property_Humidity
from homie.node.property.property_float import Property_Float
from homie.node.property.property_datetime import Property_DateTime
from homie.node.property.property_integer import Property_Integer
from homie.node.property.property_enum import Property_Enum

from .comfoairq_transformations import *
from ..comfoairq.comfoairq_const import *
from ..comfoairq.comfoairq import ComfoAirQ

import logging

logger = logging.getLogger(__name__)

CURRENT_OPERATING_MODE_SENSOR_VALUES = {
    -1  :       'auto',
     1  :       'temporary manual',
     5  :       'manual',
     6  :       'boost',
     11 :       'scheduled away',
}

CURRENT_MODE_SENSOR_VALUES = [
    'auto',
    'temporary manual',
    'manual',
    'boost',
    'scheduled away',
]

SWITCH_VALUES = {
    0  :       'OFF',
    1  :       'ON',
}

SEASONS_VALUES = {
    0  :       'INACTIVE',
    1  :       'ACTIVE',
}


FAN_MODES = {
    'away'  : CMD_FAN_MODE_AWAY     ,
    '1'     : CMD_FAN_MODE_LOW      ,
    '2'     : CMD_FAN_MODE_MEDIUM   ,
    '3'     : CMD_FAN_MODE_HIGH     ,
}

BYPASS_MODES = {
    'auto'  : CMD_BYPASS_AUTO  ,
    'on'    : CMD_BYPASS_ON    ,
    'off'   : CMD_BYPASS_OFF   ,
}

TEMPERATURE_PROFILES = {
    'normal'   : CMD_TEMPPROF_NORMAL ,
    'cool'     : CMD_TEMPPROF_COOL   ,
    'warm'     : CMD_TEMPPROF_WARM   ,
}



VENT_MODES = {
    'balance'           : [CMD_START_SUPPLY_FAN,CMD_START_EXHAUST_FAN],
    'supply only'       : [CMD_TEMPORARY_STOP_EXHAUST_FAN,CMD_START_SUPPLY_FAN],
    'extract only'      : [CMD_TEMPORARY_STOP_SUPPLY_FAN,CMD_START_EXHAUST_FAN],
    'off'               : [CMD_TEMPORARY_STOP_SUPPLY_FAN,CMD_TEMPORARY_STOP_EXHAUST_FAN],
}


OPERATING_MODES = {
    'auto'       : [CMD_MODE_MANUAL,CMD_MODE_AUTO],
    'manual'     : [CMD_MODE_MANUAL]   ,
}


MANUAL_MODE = {
    'OFF'    : CMD_MODE_AUTO     ,
    'ON'     : CMD_MODE_MANUAL   ,
}

OPERATING_MODES_SENSOR_VALUES = {
    -1  :       'auto'  ,
     1  :       'manual',
}

SENSOR_VENTILATION = [
    'off',
    'auto only',
    'on',
]

comfoairq_sensors = {
#   comfoconnect sensor         : [(    sensor_id         ,     sensor_type        ,     transformation_function, z9function_args)), ]
    SENSOR_TEMPERATURE_OUTDOOR  : [("temperature-outdoor",    "Temperature Outdoor",  "temperature" , multiply , (0.1,1,), ),],
    SENSOR_TEMPERATURE_SUPPLY   : [("temperature-supply" ,    "Temperature Supply",   "temperature" , multiply , (0.1,1,), ),],
    SENSOR_TEMPERATURE_EXTRACT  : [("temperature-extract",    "Temperature Extract",  "temperature" , multiply , (0.1,1,), ),],
    SENSOR_TEMPERATURE_EXHAUST  : [("temperature-exhaust",    "Temperature Exhaust",  "temperature" , multiply , (0.1,1,), ),],

    SENSOR_HUMIDITY_EXTRACT     : [("humidity-extract",       "Humidity Extract",     "percentage" , None     ,(),),],
    SENSOR_HUMIDITY_EXHAUST     : [("humidity-exhaust",       "Humidity Exhaust",     "percentage" , None     ,(),),],
    SENSOR_HUMIDITY_OUTDOOR     : [("humidity-outdoor",       "Humidity Outdoor",     "percentage" , None     ,(),),],
    SENSOR_HUMIDITY_SUPPLY      : [("humidity-supply",        "Humidity Supply",      "percentage" , None     ,(),),],

    SENSOR_FAN_EXHAUST_DUTY     : [("fan-exhaust-duty"        ,"Exhaust Fan Duty" ,  "percentage"  , None ,(),),
                                   ("fan-exhaust-duty-low-rate"        ,"Exhaust Fan Duty" ,  "percentage"  , slow_down ,('fan-exhaust-duty-low-rate',200,0.03,),),],
    SENSOR_FAN_SUPPLY_DUTY      : [("fan-supply-duty"         ,"Supply Fan Duty"  ,  "percentage"  , None ,(),),
                                   ("fan-supply-duty-low-rate"         ,"Supply Fan Duty"  ,  "percentage"  , slow_down ,('fan-supply-duty-low-rate',200,0.03,),),],

    SENSOR_FAN_EXHAUST_FLOW     : [("fan-exhaust-flow"     ,"Exhaust Fan Flow" ,"fan_flow"  , None ,(),),
                                   ("fan-exhaust-flow-low-rate"     ,"Exhaust Fan Flow" ,"fan_flow"  , slow_down ,('fan-exhaust-flow-low-rate',200,0.015,),),],
    SENSOR_FAN_SUPPLY_FLOW      : [("fan-supply-flow"      ,"Supply Fan Flow"  ,"fan_flow"  , None ,(),),
                                   ("fan-supply-flow-low-rate"      ,"Supply Fan Flow"  ,"fan_flow"  , slow_down ,('fan-supply-flow-low-rate',200,0.015,),),],
    SENSOR_FAN_EXHAUST_SPEED    : [("fan-exhaust-speed"    ,"Exhaust Fan Speed","fan_speed" , None ,(),),
                                   ("fan-exhaust-speed-low-rate" ,"Exhaust Fan Speed","fan_speed" , slow_down ,('fan-exhaust-speed-low-rate',200,0.015,),),],
    SENSOR_FAN_SUPPLY_SPEED     : [("fan-supply-speed"     ,"Supply Fan Speed" ,"fan_speed" , None ,(),),
                                   ("fan-supply-speed-low-rate" ,"Supply Fan Speed","fan_speed" , slow_down ,('fan-supply-speed-low-rate',200,0.015,),),],

    SENSOR_FAN_NEXT_CHANGE      : [("mode-end-date"                 ,"Operating Mode Change Date" ,"mode_end_date"                 , calculate_end_date ,(),),
                                   ("mode-timer"                    ,"Operating Mode Remaining Time" ,"mode_timer"                 , calculate_timer ,(),),],
    SENSOR_BYPASS_TIMER         : [("bypass-end-date"               ,"Bypass Manual Mode End Date" ,"mode_end_date"      , calculate_end_date ,(),),
                                   ("bypass-timer"                  ,"Bypass Manual Mode Remaining Time" ,"mode_timer"   , calculate_timer ,(),),],
    SENSOR_EXHAUST_FAN_TIMER    : [("exhaust-date"                  ,"Exhaust Fan Start Date" ,"mode_end_date"             , calculate_end_date ,(),),
                                   ("exhaust-timer"                 ,"Exhaust Fan Time to Start" ,"mode_timer"          , calculate_timer ,(),),],
    SENSOR_SUPPLY_FAN_TIMER     : [("supply-date"                   ,"Supply Fan Start Date" ,"mode_end_date"            , calculate_end_date ,(),),
                                   ("supply-timer"                  ,"Supply Fan Time to Start" ,"mode_timer"         , calculate_timer ,(),),],

    # SENSOR_OPERATING_MODE_BIS   : [("current-mode"        ,"Current Mode"     ,"enum" , transform_dict,   CURRENT_OPERATING_MODE_SENSOR_VALUES),],
    
    SENSOR_POWER_CURRENT        : [("current-power"       ,"Current Power"             ,"power_current" , None,(),),
                                   ("current-power-low-rate"       ,"Current Power"             ,"power_current" , slow_down ,('current-power-low-rate',200,0.03,),),],
    SENSOR_POWER_TOTAL_YEAR     : [("energy-ytd"          ,"Energy YTD"                ,"energy"        , None,(),),],
    SENSOR_POWER_TOTAL          : [("energy-total"        ,"Energy Total"              ,"energy"        , None,(),),],

    SENSOR_PREHEATER_POWER_CURRENT        : [("preheater-current-power"       ,"Preheater Current Power"             ,"power_current" , None,(),),
                                             ("preheater-current-power-low-rate"       ,"Preheater Current Power"             ,"power_current" , slow_down ,('preheater-current-power-low-rate',20,0.03,),),],
    SENSOR_PREHEATER_POWER_TOTAL_YEAR     : [("preheater-energy-ytd"          ,"Preheater Energy YTD"                ,"energy"        , None,(),),],
    SENSOR_PREHEATER_POWER_TOTAL          : [("preheater-energy-total"        ,"Preheater Energy Total"              ,"energy"        , None,(),),],

    SENSOR_AVOIDED_HEATING_CURRENT        : [("avoided-heating-current-power"      ,"Avoided Heating Current Power"             ,"power_current" , None,(),),
                                             ("avoided-heating-current-power-low-rate"      ,"Avoided Heating Current Power"             ,"power_current" , slow_down ,('avoided-heating-current-power-low-rate',20,0.03,),),],
    SENSOR_AVOIDED_HEATING_TOTAL_YEAR     : [("avoided-heating-energy-ytd"          ,"Avoided Heating Energy YTD"                ,"energy"        , None,(),),],
    SENSOR_AVOIDED_HEATING_TOTAL          : [("avoided-heating-energy-total"        ,"Avoided Heating Energy Total"              ,"energy"        , None,(),),],

    SENSOR_AVOIDED_COOLING_CURRENT        : [("avoided-cooling-current-power"       ,"Avoided Cooling Current Power"             ,"power_current" , None,(),),
                                             ("avoided-cooling-current-power-low-rate"       ,"Avoided Cooling Current Power"             ,"power_current" , slow_down ,('avoided-cooling-current-power-low-rate',20,0.03,),),],
    SENSOR_AVOIDED_COOLING_TOTAL_YEAR     : [("avoided-cooling-energy-ytd"          ,"Avoided Cooling Energy YTD"                ,"energy"        , None,(),),],
    SENSOR_AVOIDED_COOLING_TOTAL          : [("avoided-cooling-energy-total"        ,"Avoided Cooling Energy Total"              ,"energy"        , None,(),),],

    SENSOR_DAYS_TO_REPLACE_FILTER         : [("filter-replace"          ,"Filter replace" ,"integer" , None ,(),),],

    SENSOR_CURRENT_RMOT                   : [("current-rmot"            ,"Running Mean Outdoor Temperature"   ,"temperature" , multiply , (0.1,1,), ),],
    SENSOR_BYPASS_STATE                   : [("bypass-state"            ,"Bypass state"   ,"percentage" , None ,(),),],

    SENSOR_HEATING_SEASON                 : [("heating-season"          ,"Heating Season" ,"enum" , transform_dict ,SEASONS_VALUES,),],
    SENSOR_COOLING_SEASON                 : [("cooling-season"          ,"Cooling Season" ,"enum" , transform_dict ,SEASONS_VALUES,),],
}

repeating_timer = None

class Device_ComfoAirQ(Device_Base):

    comfoairq = None
    comfoairq_controls = {}

    flow_presets = {}

    exhaust_fan_stopped = 0
    supply_fan_stopped = 0

    operating_mode_bis = None
    operating_mode = None

    min_low_flow = None
    max_high_flow = None

    def __init__(
                self, 
                device_id=None, 
                name=None, 
                homie_settings=None, 
                mqtt_settings=None,
                sensors_definition = comfoairq_sensors,
                comfoconnect_settings=None,                
    ):
        assert comfoconnect_settings
        assert mqtt_settings

        super().__init__ (device_id, name, homie_settings, mqtt_settings)

        self.state = 'init'
        global repeating_timer
        if repeating_timer == None:
            repeating_timer = Repeating_Timer(
                self.homie_settings["update_interval"]
            )

        repeating_timer.add_callback(self.publish_connection_status)

        self.sensors = sensors_definition
        self.comfoconnect_settings=comfoconnect_settings
        self.min_low_flow = self.comfoconnect_settings['COMFOCONNECT_MIN_LOW_FLOW']

        self.max_high_flow = self.comfoconnect_settings['COMFOCONNECT_MAX_HIGH_FLOW']

        self.comfoairq = ComfoAirQ(comfoconnect_settings=self.comfoconnect_settings)
        self.comfoairq.callback_sensor = self.callback_sensor

        self.comfoairq.add_on_state_change_callback(self.publish_connection_status)

# Sensors

        node = Node_Base(self,'sensors','Sensors','sensors')
        self.add_node (node)

        for comfoairq_sensor in self.sensors:
            self.comfoairq.register_sensor(comfoairq_sensor)
            for homie_sensor in self.sensors[comfoairq_sensor]:
                sensor_id ,sensor_name ,sensor_type, transformation_function, function_args =  homie_sensor
                if sensor_type == 'temperature':
                    node.add_property (Property_Temperature (node,id=sensor_id,name = sensor_name, unit='°C'))
                elif sensor_type == 'fan_speed':
                    node.add_property (Property_Float (node,id=sensor_id,name = sensor_name,settable = False,unit='rpm'))
                elif sensor_type == 'fan_flow':
                    node.add_property (Property_Float (node,id=sensor_id,name = sensor_name,settable = False,unit='m³/h'))
                elif sensor_type == 'percentage':
                    node.add_property (Property_Float (node,id=sensor_id,name = sensor_name,settable = False,unit='%'))
                elif sensor_type == 'mode_end_date':
                    node.add_property (Property_DateTime (node,id=sensor_id,name = sensor_name,settable = False,data_format='%Y-%m-%d %H:%M:%S.%f'))
                elif sensor_type == 'mode_timer':
                    node.add_property (Property_Integer (node,id=sensor_id,name = sensor_name,settable = False,unit='s'))
                elif sensor_type == 'enum':
                    node.add_property (Property_Enum (node,id=sensor_id,name = sensor_name,settable = False,data_format=','.join(function_args.values())))
                elif sensor_type == 'power_current':
                    node.add_property (Property_Float (node,id=sensor_id,name = sensor_name,settable = False,unit='W'))
                elif sensor_type == 'energy':
                    node.add_property (Property_Float (node,id=sensor_id,name = sensor_name,settable = False,unit='kWh'))
                elif sensor_type == 'integer':
                    node.add_property (Property_Integer(node,id=sensor_id,name = sensor_name,settable = False))

# Sensors managed same way as Controls 

        node.add_property(Property_Enum (node,id='current-mode',name ='Current Mode',settable = False,data_format=','.join(CURRENT_OPERATING_MODE_SENSOR_VALUES.values())))
        self.add_controls_callback(SENSOR_OPERATING_MODE_BIS,self.update_current_mode)
        self.add_controls_callback(SENSOR_OPERATING_MODE,self.update_current_mode)

# Controls

        node = Node_Base(self,'controls','Controls','controls')
        self.add_node (node)

# FAN SPEED MODE
        node.add_property(Property_Enum (node,id='fan-mode',name='Fan Mode',data_format=','.join(FAN_MODES.keys()),set_value = lambda value: self.set_fan_mode(value)))
        self.add_controls_callback(SENSOR_FAN_SPEED_MODE,self.update_fan_mode)

# BYPASS  MODE (for 1 hour)
        node.add_property(Property_Enum (node,id='bypass-mode',name='Bypass Mode',data_format=','.join(BYPASS_MODES.keys()),set_value = lambda value: self.set_bypass_mode(value)))
        self.add_controls_callback(SENSOR_BYPASS_MODE,self.update_bypass_mode)

# BYPASS ON 
        node.add_property(Property_Integer (node,id='bypass-on', name='Bypass On',data_format='0:'+ str(0xffffffff),set_value = lambda value: self.set_bypass_on(value)))
# BYPASS OFF
        node.add_property(Property_Integer (node,id='bypass-off', name='Bypass Off',data_format='0:'+ str(0xffffffff),set_value = lambda value: self.set_bypass_off(value)))

        self.add_controls_callback(SENSOR_BYPASS_MODE,self.update_bypass)
        self.add_controls_callback(SENSOR_BYPASS_TIMER,self.update_bypass)

# TEMPERATURE PROFILE
        node.add_property(Property_Enum (node,id='temperature-profile',name='Temperature Profile',data_format=','.join(TEMPERATURE_PROFILES.keys()),set_value = lambda value: self.set_temperature_profile(value)))
        self.add_controls_callback(SENSOR_TEMPERATURE_PROFILE,self.update_temperature_profile)

# OPERATING MODE
        node.add_property(Property_Enum (node,id='operating-mode',name='Operating Mode',data_format=','.join(OPERATING_MODES.keys()),set_value = lambda value: self.set_operating_mode(value)))
        self.add_controls_callback(SENSOR_OPERATING_MODE,self.update_operating_mode)

# Manual MODE
        node.add_property(Property_Switch (node,id='manual-mode',name='Manual Mode',set_value = lambda value: self.set_manual_mode(value)))
        self.add_controls_callback(SENSOR_OPERATING_MODE,self.update_manual_mode)

# VENT MODE
        node.add_property(Property_Enum (node,id='vent-mode',name='Ventilation Mode',data_format=','.join(VENT_MODES.keys()),set_value = lambda value: self.set_vent_mode(value)))
        self.add_controls_callback(SENSOR_TEMPORARY_STOP_EXHAUST_FAN_STATE,self.update_vent_mode)
        self.add_controls_callback(SENSOR_TEMPORARY_STOP_SUPPLY_FAN_STATE,self.update_vent_mode)

# SUPPLY FAN OFF 
        node.add_property(Property_Integer (node,id='supply-fan-off', name='Supply Fan Off',data_format='0:'+ str(0xffffffff),set_value = lambda value: self.set_supply_fan_off(value)))
        self.add_controls_callback(SENSOR_SUPPLY_FAN_TIMER,self.update_supply_fan_off)

# EXHAUST FAN  OFF
        node.add_property(Property_Integer (node,id='exhaust-fan-off', name='Exhaust Fan Off',data_format='0:'+ str(0xffffffff),set_value = lambda value: self.set_exhaust_fan_off(value)))
        self.add_controls_callback(SENSOR_EXHAUST_FAN_TIMER,self.update_exhaust_fan_off)

# BOOST MODE
        node.add_property(Property_Integer (node,id='boost-mode',name='Activate Scheduled Boost Mode',data_format='0:'+ str(0xffffffff),set_value = lambda value: self.set_boost_mode(value)))
        self.add_controls_callback(SENSOR_OPERATING_MODE_BIS,self.update_boost_mode)
        self.add_controls_callback(SENSOR_FAN_NEXT_CHANGE,self.update_boost_mode)

# AWAY MODE
        node.add_property(Property_Integer (node,id='away-mode',name='Activate Scheduled Away Mode',data_format='0:'+ str(0xffffffff),set_value = lambda value: self.set_away_mode(value)))
        self.add_controls_callback(SENSOR_OPERATING_MODE_BIS,self.update_away_mode)
        self.add_controls_callback(SENSOR_FAN_NEXT_CHANGE,self.update_away_mode)

# Heating Season detection RMOT
        node.add_property(Property_Temperature (node,id='heating-rmot',name='Heating Limit RMOT',data_format='0:20',unit='°C',settable = True, set_value = lambda value: self.set_heating_rmot(value)))
        self.comfoairq.add_on_state_change_callback(self.update_heating_rmot)
        repeating_timer.add_callback(self.update_heating_rmot)

# Cooling Season detection RMOT
        node.add_property(Property_Temperature (node,id='cooling-rmot',name='Cooling Limit RMOT',data_format='15:40',unit='°C',settable = True, set_value = lambda value: self.set_cooling_rmot(value)))
        self.comfoairq.add_on_state_change_callback(self.update_cooling_rmot)
        repeating_timer.add_callback(self.update_cooling_rmot)

#Temperature  passive
        node.add_property(Property_Enum (node,id='temperature-passive',name='Temperature Passive',data_format=','.join(SENSOR_VENTILATION),set_value = lambda value: self.set_temperature_passive(value)))
        self.comfoairq.add_on_state_change_callback(self.update_temperature_passive)
        repeating_timer.add_callback(self.update_temperature_passive)

#Humidity comfort
        node.add_property(Property_Enum (node,id='humidity-comfort',name='Humidity Comfort',data_format=','.join(SENSOR_VENTILATION),set_value = lambda value: self.set_humidity_comfort(value)))
        self.comfoairq.add_on_state_change_callback(self.update_humidity_comfort)
        repeating_timer.add_callback(self.update_humidity_comfort)

#Humidity protection
        node.add_property(Property_Enum (node,id='humidity-protection',name='Humidity Protection',data_format=','.join(SENSOR_VENTILATION),set_value = lambda value: self.set_humidity_protection(value)))
        self.comfoairq.add_on_state_change_callback(self.update_humidity_protection)
        repeating_timer.add_callback(self.update_humidity_protection)

#Flow unbalance
        node.add_property(Property_Float (node,id='unbalance',name='Flow Unbalance',data_format='-15:15',set_value = lambda value: self.set_unbalance(value)))
        self.comfoairq.add_on_state_change_callback(self.update_unbalance)
        repeating_timer.add_callback(self.update_unbalance)

#Flow Away
        node.add_property(Property_Integer (node,id='flow-away',name='Flow Away Speed',data_format='0:' + str(self.max_high_flow),set_value = lambda value: self.set_flow_away(value)))
        self.comfoairq.add_on_state_change_callback(self.update_flow_away)
        repeating_timer.add_callback(self.update_flow_away)

#Flow Low
        node.add_property(Property_Integer (node,id='flow-low',name='Flow Low Speed',data_format= str(self.min_low_flow) + ':' + str(self.max_high_flow),set_value = lambda value: self.set_flow_low(value)))
        self.comfoairq.add_on_state_change_callback(self.update_flow_low)
        repeating_timer.add_callback(self.update_flow_low)

#Flow Medium
        node.add_property(Property_Integer (node,id='flow-medium',name='Flow Medium Speed',data_format=str(self.min_low_flow) + ':' + str(self.max_high_flow),set_value = lambda value: self.set_flow_medium(value)))
        self.comfoairq.add_on_state_change_callback(self.update_flow_medium)
        repeating_timer.add_callback(self.update_flow_medium)

#Flow High
        node.add_property(Property_Integer (node,id='flow-high',name='Flow High Speed',data_format=str(self.min_low_flow) + ':' + str(self.max_high_flow),set_value = lambda value: self.set_flow_high(value)))
        self.comfoairq.add_on_state_change_callback(self.update_flow_high)
        repeating_timer.add_callback(self.update_flow_high)

        self.start()
        self.publish_connection_status()

    def exit(self):
        self.comfoairq.exit()

    def connect(self):
        self.comfoairq.connect()

    def disconnect(self):
        self.comfoairq.disconnect()

    def set_fan_mode(self,value):
        # print ("Fan mode: %s" % (value))
        self.comfoairq.cmd_rmi_request(FAN_MODES.get(value))

    def update_fan_mode(self,var,value):
        self.get_node('controls').get_property('fan-mode').value  = list(FAN_MODES.keys())[value]

    def set_bypass_mode(self,value):
        self.comfoairq.cmd_rmi_request(BYPASS_MODES.get(value))

    def update_bypass_mode(self,var,value):
        self.get_node('controls').get_property('bypass-mode').value  = list(BYPASS_MODES.keys())[value]

    def set_temperature_profile(self,value):
        self.comfoairq.cmd_rmi_request(TEMPERATURE_PROFILES.get(value))

    def update_temperature_profile(self,var,value):
        self.get_node('controls').get_property('temperature-profile').value  = list(TEMPERATURE_PROFILES.keys())[value]


    def set_operating_mode(self,value):
        for command in OPERATING_MODES.get(value):
            self.comfoairq.cmd_rmi_request(command)

    def update_operating_mode(self,var,value):
        # if var == SENSOR_OPERATING_MODE:
        if value in OPERATING_MODES_SENSOR_VALUES.keys():
            self.get_node('controls').get_property('operating-mode').value  = OPERATING_MODES_SENSOR_VALUES[value]

    def set_manual_mode(self,value):
        logger.info("Setting manual mode: %s" % (value))
        self.comfoairq.cmd_rmi_request(MANUAL_MODE.get(value))

    def update_manual_mode(self,var,value):
        # if var == SENSOR_OPERATING_MODE:
        if value == 1:            
             self.get_node('controls').get_property('manual-mode').value  = 'ON'
        else:
             self.get_node('controls').get_property('manual-mode').value  = 'OFF'

    def set_vent_mode(self,value):
        # logger.info("vent mode to set : {} with command: {} ".format(value,VENT_MODES.get(value)))
        for command in VENT_MODES.get(value):
            self.comfoairq.cmd_rmi_request(command)

    def update_vent_mode(self,var,value):
        if var == SENSOR_TEMPORARY_STOP_SUPPLY_FAN_STATE:
            self.supply_fan_stopped = value
        if var == SENSOR_TEMPORARY_STOP_EXHAUST_FAN_STATE:
            self.exhaust_fan_stopped = value
        
        if self.exhaust_fan_stopped == 0 and self.supply_fan_stopped == 0:
            self.get_node('controls').get_property('vent-mode').value  = list(VENT_MODES.keys())[0] # balance 
        if self.exhaust_fan_stopped == 1 and self.supply_fan_stopped == 0:
            self.get_node('controls').get_property('vent-mode').value  = list(VENT_MODES.keys())[1] # supply only
        if self.exhaust_fan_stopped == 0 and self.supply_fan_stopped == 1:
            self.get_node('controls').get_property('vent-mode').value  = list(VENT_MODES.keys())[2] # extract only
        if self.exhaust_fan_stopped == 1 and self.supply_fan_stopped == 1:
            self.get_node('controls').get_property('vent-mode').value  = list(VENT_MODES.keys())[3] # extract only


    def set_supply_fan_off(self,value):
        self.comfoairq.cmd_rmi_request(b'\x84\x15\x07\x01\x00\x00\x00\x00' + struct.pack('<i',value) + b'\x01')

    def set_exhaust_fan_off(self,value):
        self.comfoairq.cmd_rmi_request(b'\x84\x15\x06\x01\x00\x00\x00\x00' + struct.pack('<i',value) + b'\x01')

    def update_supply_fan_off(self,var,value):
        self.get_node('controls').get_property('supply-fan-off').value = calculate_timer(None,value,None)
    
    def update_exhaust_fan_off(self,var,value):
        self.get_node('controls').get_property('exhaust-fan-off').value = calculate_timer(None,value,None)

    def set_bypass_on(self,value):
        self.comfoairq.cmd_rmi_request(b'\x84\x15\x02\x01\x00\x00\x00\x00' + struct.pack('<i',value) + b'\x01')

    def set_bypass_off(self,value):
        self.comfoairq.cmd_rmi_request(b'\x84\x15\x02\x01\x00\x00\x00\x00' + struct.pack('<i',value) + b'\x02')

    def update_bypass(self,var,value):        
        if self.get_node('controls').get_property('bypass-mode').value == list(BYPASS_MODES.keys())[1]: #bypass on
            self.get_node('controls').get_property('bypass-on').value = self.get_node('sensors').get_property('bypass-timer').value
        else:
            self.get_node('controls').get_property('bypass-on').value = 0

        if self.get_node('controls').get_property('bypass-mode').value == list(BYPASS_MODES.keys())[2]: #bypass off
            self.get_node('controls').get_property('bypass-off').value = self.get_node('sensors').get_property('bypass-timer').value
        else:
            self.get_node('controls').get_property('bypass-off').value = 0

    def set_boost_mode(self,value):
        self.comfoairq.cmd_rmi_request(b'\x84\x15\x01\x06\x00\x00\x00\x00' + struct.pack('<i',value) + b'\x03')

    def update_boost_mode(self,var,value):
        if self.get_node('sensors').get_property('current-mode').value == CURRENT_MODE_SENSOR_VALUES[3]: #boost
            self.get_node('controls').get_property('boost-mode').value = self.get_node('sensors').get_property('mode-timer').value
        else:
            self.get_node('controls').get_property('boost-mode').value = 0

    def set_away_mode(self,value):
        self.comfoairq.cmd_rmi_request(b'\x84\x15\x01\x0b\x00\x00\x00\x00' + struct.pack('<i',value) + b'\x00')                                                      

    def update_away_mode(self,var,value):
        if self.get_node('sensors').get_property('current-mode').value == CURRENT_MODE_SENSOR_VALUES[4]:
            self.get_node('controls').get_property('away-mode').value = self.get_node('sensors').get_property('mode-timer').value
        else:
            self.get_node('controls').get_property('away-mode').value = 0

    def update_current_mode(self,var,value):
        if var == SENSOR_OPERATING_MODE_BIS:
            self.operating_mode_bis = value
        if var == SENSOR_OPERATING_MODE:
            self.operating_mode = value

        if self.operating_mode == -1:
            if self.operating_mode_bis == -1:
                self.get_node('sensors').get_property('current-mode').value  = CURRENT_MODE_SENSOR_VALUES[0] # auto
            elif self.operating_mode_bis == 1:
                self.get_node('sensors').get_property('current-mode').value  = CURRENT_MODE_SENSOR_VALUES[1] # temporary manual
        
        if self.operating_mode_bis == 6 :
                self.get_node('sensors').get_property('current-mode').value  = CURRENT_MODE_SENSOR_VALUES[3] # boost
        elif  self.operating_mode_bis == 11 :
                self.get_node('sensors').get_property('current-mode').value  = CURRENT_MODE_SENSOR_VALUES[4] # scheduled away
        elif  self.operating_mode_bis in [1,5] and  self.operating_mode == 1:
                self.get_node('sensors').get_property('current-mode').value  = CURRENT_MODE_SENSOR_VALUES[2] # temporary manual

    def set_heating_rmot(self,value):
        val = int(10 * value)
        self.comfoairq.cmd_rmi_request(b'\x03\x1d\x01\x02' + struct.pack('h',val))
        time.sleep(1)
        self.update_heating_rmot()

    def update_heating_rmot(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1d\x01\x10\x02')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.get_node('controls').get_property('heating-rmot').value = round(val * 0.1,1)

    def set_cooling_rmot(self,value):
        val = int(10 * value)
        self.comfoairq.cmd_rmi_request(b'\x03\x1d\x01\x03' + struct.pack('h',val))
        time.sleep(1)
        self.update_heating_rmot()

    def update_cooling_rmot(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1d\x01\x10\x03')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.get_node('controls').get_property('cooling-rmot').value = round(val * 0.1,1)
    
    def set_temperature_passive(self,value):
        self.comfoairq.cmd_rmi_request(b'\x03\x1d\x01\x04' + struct.pack('B',SENSOR_VENTILATION.index(value)))
        time.sleep(1)
        self.update_temperature_passive()

    def update_temperature_passive(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1d\x01\x10\x04')
        if reply_message is not None:
            val = struct.unpack('B', reply_message.msg.message)[0]
            self.get_node('controls').get_property('temperature-passive').value = SENSOR_VENTILATION[val]

    def set_humidity_comfort(self,value):
        self.comfoairq.cmd_rmi_request(b'\x03\x1d\x01\x06' + struct.pack('B',SENSOR_VENTILATION.index(value)))
        time.sleep(1)
        self.update_temperature_passive()

    def update_humidity_comfort(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1d\x01\x10\x06')
        if reply_message is not None:
            val = struct.unpack('B', reply_message.msg.message)[0]
            self.get_node('controls').get_property('humidity-comfort').value = SENSOR_VENTILATION[val]

    def set_humidity_protection(self,value):
        self.comfoairq.cmd_rmi_request(b'\x03\x1d\x01\x07' + struct.pack('B',SENSOR_VENTILATION.index(value)))
        time.sleep(1)
        self.update_temperature_passive()

    def update_humidity_protection(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1d\x01\x10\x07')
        if reply_message is not None:
            val = struct.unpack('B', reply_message.msg.message)[0]
            self.get_node('controls').get_property('humidity-protection').value = SENSOR_VENTILATION[val]

    def set_unbalance(self,value):
        val = int(10 * value)
        self.comfoairq.cmd_rmi_request(b'\x03\x1e\x01\x12' + struct.pack('h',val))
        time.sleep(1)
        self.update_unbalance()

    def update_unbalance(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1e\x01\x10\x12')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.get_node('controls').get_property('unbalance').value = round(val * 0.1,1)

    def set_flow_away(self,value):
        val = int(value)
        if ( 'low' in self.flow_presets.keys() and value <= self.flow_presets['low']):
            try:
                self.comfoairq.cmd_rmi_request(b'\x03\x1e\x01\x03' + struct.pack('h',val))
            except (Exception) as ex:
                logger.info(ex)
        time.sleep(1)
        self.update_flow_away()
        self.update_flow_low()
        self.update_flow_medium()
        self.update_flow_high()

    def set_flow_low(self,value):
        val = int(value)
        if ( 'medium' in self.flow_presets.keys() and value <= self.flow_presets['medium']):
            try:
                self.comfoairq.cmd_rmi_request(b'\x03\x1e\x01\x04' + struct.pack('h',val))
            except (Exception) as ex:
                logger.info(ex)
        time.sleep(1)
        self.update_flow_away()
        self.update_flow_low()
        self.update_flow_medium()
        self.update_flow_high()

    def set_flow_medium(self,value):
        val = int(value)
        if ( 'high' in self.flow_presets.keys() and value <= self.flow_presets['high']):
            try:
                self.comfoairq.cmd_rmi_request(b'\x03\x1e\x01\x05' + struct.pack('h',val))
            except (Exception) as ex:
                logger.info(ex)
        time.sleep(1)
        self.update_flow_away()
        self.update_flow_low()
        self.update_flow_medium()
        self.update_flow_high()

    def set_flow_high(self,value):
        val = int(value)
        if ( 'medium' in self.flow_presets.keys() and value >= self.flow_presets['medium']):
            try:
                self.comfoairq.cmd_rmi_request(b'\x03\x1e\x01\x06' + struct.pack('h',val))
            except (Exception) as ex:
                logger.info(ex)
        time.sleep(1)
        self.update_flow_away()
        self.update_flow_low()
        self.update_flow_medium()
        self.update_flow_high()

    def update_flow_away(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1e\x01\x10\x03')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.flow_presets['away']=val
            self.get_node('controls').get_property('flow-away').value = val

    def update_flow_low(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1e\x01\x10\x04')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.flow_presets['low']=val
            self.get_node('controls').get_property('flow-low').value = val

    def update_flow_medium(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1e\x01\x10\x05')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.flow_presets['medium']=val
            self.get_node('controls').get_property('flow-medium').value = val

    def update_flow_high(self):
        reply_message = self.comfoairq.cmd_rmi_request(b'\x01\x1e\x01\x10\x06')
        if reply_message is not None:
            val = struct.unpack('h', reply_message.msg.message)[0]
            self.flow_presets['high']=val
            self.get_node('controls').get_property('flow-high').value = val

    def add_controls_callback(self,sensor,callback):
        self.comfoairq.register_sensor(sensor)
        if sensor not in self.comfoairq_controls:
            self.comfoairq_controls[sensor] = [callback]
        else:
            self.comfoairq_controls[sensor].append(callback)

    def callback_sensor(self,var, value):
    ## Callback sensors ################################################################################################
        if var in self.sensors:
            for homie_sensor in self.sensors.get(var):
                sensor_id ,sensor_name ,sensor_type , transformation_function, function_args  =  homie_sensor

                if transformation_function is None:
                    self.get_node('sensors').get_property(sensor_id).value  = value
                else:
                    ret_value = transformation_function(var,value,function_args)
                    if ret_value is not None:
                        self.get_node('sensors').get_property(sensor_id).value  = ret_value
        if var in self.comfoairq_controls:
            for callback in self.comfoairq_controls[var]:
                callback(var,value)


    def publish_connection_status(self):
        if self.comfoairq is None:
            self.state = 'alert'
        elif self.comfoairq._exit:
            self.state = 'disconnected'
        elif self.comfoairq._stay_connected == False:
            self.state = 'sleeping'
        elif self.comfoairq.comfoconnect_bridge is None:
            self.state = 'alert'
        elif self.comfoairq.comfoconnect.is_connected() == False:
            self.state = 'alert'
        else:
            self.state = 'ready'
            
