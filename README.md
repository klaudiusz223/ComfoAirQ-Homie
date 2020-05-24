# ComfoAirQ-Homie
**Homie4 for Zehnder ComfoAirQ350/450/600 ventilation units**

Uses pycomfoconnect (https://github.com/michaelarnauts/comfoconnect/) and Homie4 (https://github.com/mjcumming/homie4).

## Installation:


Preequirements:

Python >= 3.6
<br/>
MQTT broker - Tested with mosquitto https://mosquitto.org/
<br/>
Python  Wheels

pycomfoconnect library from master branch. Version from PyPI repository is too old.
<br/>
Tested with
https://github.com/michaelarnauts/comfoconnect.git#97093b8b50710107c96eb101f2db83ae0f2ddfaf



```
pip3 install wheel
pip3 install --upgrade git+https://github.com/michaelarnauts/comfoconnect.git@97093b8b50710107c96eb101f2db83ae0f2ddfaf'
pip3 install git+https://github.com/klaudiusz223/ComfoAirQ-Homie.git
```

Create configuration in comfoairq_homie.yml file. ComfoAirQ-Homie searches this file in directory from which is started or it is possible to specify it by command line option "-c filename.yml". 

```
mqtt:
  MQTT_BROKER: "192.168.88.10"
  MQTT_PORT: 1883
  MQTT_USERNAME: null
  MQTT_PASSWORD: null
  MQTT_KEEPALIVE: 60
  MQTT_CLIENT_ID: null
  MQTT_SHARE_CLIENT: False

comfoconnect:
  COMFOCONNECT_HOST : null
  COMFOCONNECT_PIN  : 0
  COMFOCONNECT_NAME : "ComfoConnect Homie Gateway"
  COMFOCONNECT_UUID : "00000000000000000000000000000006"
  COMFOCONNECT_AUTOCONNECT : True

comfoairq_homie:
  HOMIE_ID              : zehnderq450
  HOMIE_NAME            : ZehnderQ450
```


## Usage examples:

```
comfoairq-homie
```
or
```
python3 -m comfoairq_homie
```

specifying config file, logging to additional file 

```
comfoairq-homie -c config_file.yml -l optional_log_file.log
```


Seting log level using environment variables. Different log level for pycomfoconnect library and other libraries 
```
COMFOAIRQ_LOGLEVEL=ERROR  COMFOAIRQ_COMFOCONNECT_LOGLEVEL=DEBUG comfoairq-homie -c comfoairq_homie.yml -l comfoairq_homie.log
```
## Systemd service file example:
```
[Unit]
Description="Homie4 ComfoAirQ Service"
After=syslog.target network.target mosquitto.service openhab2.service


[Service]
WorkingDirectory=/opt/comfoairq/
Environment=COMFOAIRQ_LOGLEVEL=INFO
Environment=COMFOAIRQ_COMFOCONNECT_LOGLEVEL=INFO
Environment=PATH=/opt/comfoairq/virtualenv/bin:$PATH
ExecStart=/opt/comfoairq/virtualenv/bin/comfoairq-homie -c /opt/comfoairq/config/comfoairq_homie.yml -l /opt/comfoairq/log/comfoairq_homie.log
Restart=always

[Install]
WantedBy=multi-user.target
```