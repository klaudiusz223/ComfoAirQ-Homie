import yaml
import time
import os
import sys
import signal
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler


from .comfoairq_homie import ComfoAirQ_Homie
from . import __version__

def handle_exit(sig, frame):
    raise(SystemExit)

def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument("-c", "--config", help = "config file. Default: comfoairq_homie.yml ", default="./comfoairq_homie.yml") 
    parser.add_argument("-l", "--logfile", help = "optional log file" ) 
  
    args = parser.parse_args() 

    signal.signal(signal.SIGTERM, handle_exit)

    logger = logging.getLogger(__name__)
    
    FORMATTER = logging.Formatter("%(asctime)s - [%(name)s]  [%(levelname)s]  %(message)s")    
    LOGLEVEL = os.environ.get('COMFOAIRQ_LOGLEVEL','INFO').upper()
    LOGLEVEL_COMFOCONNECT = os.environ.get('COMFOAIRQ_COMFOCONNECT_LOGLEVEL', LOGLEVEL).upper()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    logging.getLogger('bridge').setLevel(LOGLEVEL_COMFOCONNECT)
    logging.getLogger('pycomfoconnect').setLevel(LOGLEVEL_COMFOCONNECT)


    if args.logfile is not None:
        file_handler = TimedRotatingFileHandler(args.logfile, when="midnight")
        file_handler.setFormatter(FORMATTER)
        logger.addHandler(file_handler)
        logging.basicConfig(level=LOGLEVEL,handlers=[file_handler,console_handler])
    else: 
        logging.basicConfig(level=LOGLEVEL,handlers=[console_handler])

  
    with open(args.config, 'r') as ymlfile:
        cfg = yaml.full_load(ymlfile)

    try:
        logger.info('Starting ComfoAirQ-Homie version {}'.format(__version__))
        logger.info('Waiting... Stop with CTRL+C')

        caqh = ComfoAirQ_Homie( 
                                device_id=cfg['comfoairq_homie']['HOMIE_ID'], 
                                name = cfg['comfoairq_homie']['HOMIE_NAME'],
                                mqtt_settings=cfg['mqtt'],
                                comfoconnect_settings = cfg['comfoconnect'],
        )
        
        while True:
            time.sleep(10)

    except (KeyboardInterrupt,SystemExit) as ex:
        if caqh is not None:
            caqh.exit()
        time.sleep(0.2)
        logger.info ("Bye")
        pass

if __name__ == "__main__":
    main()
