import argparse
from src import move_detection as MV
from pathlib import Path
import yaml
from src import utils 

def main():
    path = Path('config.yaml')
    with path.open('r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    detector = MV.MotionDetector(config)
    detector.detect('write')
    logger = detector.get_log_logger()
    logger.log_info('detecting started')
    while not config['RELEASE_CAPTURE']:

        with path.open('r', encoding='utf-8') as f:
            config =yaml.safe_load(f)
    detector.release()
    logger.info('detecting ended, capture released')    

if __name__ == '__main__':
    main()

