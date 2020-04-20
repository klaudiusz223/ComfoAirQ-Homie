# ComfoAirQ-Homie
**Homie4 for Zehnder ComfoAirQ350/450/600 ventilation units**

Uses pycomfoconnect (https://github.com/michaelarnauts/comfoconnect/) and Homie4 (https://github.com/mjcumming/homie4) .<br/>

## Installation:

ComfoAirQ-Homie requires pycomfoconnect library from master branch. Version from PyPI repository is too old
But currently recommended version of pycomfoconnect is https://github.com/jonesPD/comfoconnect/tree/patch-3 - also cloned to https://github.com/klaudiusz223/comfoconnect/tree/patch-3

```
pip3 install --upgrade git+https://github.com/klaudiusz223/comfoconnect.git@patch-3
pip3 install git+https://github.com/klaudiusz223/ComfoAirQ-Homie.git
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
