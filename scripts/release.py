import argparse
from pathlib import Path
import yaml

# этот скрипт реализует логику отключения capture от rtsp потока из VideoDetector из move_detection.py
parser = argparse.ArgumentParser()
parser.add_argument(
        '--release', 
        type = str,
        help ='releas video capture if release == Yes or yes',
        required= True
    )


namespace = parser.parse_args()
release = True if namespace.release in ['Yes', 'yes'] else False

path = Path('config.yaml')
with path.open('r',encoding='utf-8') as f:
    config = yaml.safe_load(f)

config['RELEASE_CAPTURE'] = True

with path.open('w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

