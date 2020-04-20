# ComfoAirQ-Homie
**Homie4 for Zehnder ComfoAirQ**

Uses pycomfoconnect library (https://github.com/michaelarnauts/comfoconnect/tree/master/pycomfoconnect) .<br/>
Currently recommended version of pycomfoconnect is https://github.com/jonesPD/comfoconnect/tree/patch-3 - also cloned to https://github.com/klaudiusz223/comfoconnect/tree/patch-3

## Installation:

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
