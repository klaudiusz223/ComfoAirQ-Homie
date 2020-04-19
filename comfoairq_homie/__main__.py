import yaml
import time
import os
import sys
import argparse

from .comfoairq_homie import ComfoAirQ_Homie

import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = os.path.expanduser("~") + "/comfoairqhomie.log"

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(FORMATTER)

file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
file_handler.setFormatter(FORMATTER)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logging.basicConfig(level=logging.INFO,handlers=[file_handler,console_handler])
# logging.basicConfig(level=logging.DEBUG,handlers=[file_handler,console_handler])


def main():

    parser = argparse.ArgumentParser() 
    parser.add_argument("-c", "--config", help = "Config File. Default: comfoairq_homie.yml ", default="comfoairq_homie.yml") 
  
    args = parser.parse_args() 
  
    with open(args.config, 'r') as ymlfile:
        cfg = yaml.full_load(ymlfile)

    try:
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
        caqh.exit()
        time.sleep(0.2)
        logger.info ("Bye")
        pass

if __name__ == "__main__":
    main()