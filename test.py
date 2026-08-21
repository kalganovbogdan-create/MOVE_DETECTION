import yaml
from pathlib import Path
import cv2

path =Path('config.yaml')
with path.open('r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
print(config)
