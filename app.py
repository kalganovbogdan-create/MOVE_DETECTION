from src import move_detection as MV
from pathlib import Path
import yaml
import cv2 as cv

with Path('config.yaml').open('r',encoding='utf-8') as file:
    config = yaml.safe_load(file)

detector = MV.MotionDetector(config)
log_path = config['LOGGER_PATH_TO_LOG_FILE']
csv_path = config['LOGGER_PATH_TO_CSV_FILE']
storage_path = config['VIDEO_STORAGE_PATH']
logger = MV.VideoLogger(log_path, csv_path,storage_path)
reader = MV.VideoReader(logger = logger.logger,Logger=logger, config=config)
reader.start_capture(config['RTSP_URL'])
buffer_generator = reader.write_buffer(logger.csv_logger)
frame_generator = reader.read()
next(frame_generator)

W = int(reader.capture.get(cv.CAP_PROP_FRAME_WIDTH)) 
H = int(reader.capture.get(cv.CAP_PROP_FRAME_HEIGHT))

if H == 0:
    raise ValueError('H == 0')
elif  W == 0:
    raise ValueError('W == 0')
else:
    print(W,H)
def main():

    while reader.capture.isOpened():
        try:
            if not reader.capture.isOpened():
                break
        except:
            break
        buffer, motion_id  = next(buffer_generator)
        fps = reader.capture.get(cv.CAP_PROP_FPS) or 10
        
        #buffer,motion_id,fps,W,H    
        logger.save_motion(frame_buffer=buffer,
                           motion_id=motion_id,
                           fps = fps,
                           W = W,
                           H = H)

    try:    
        reader.release_capture()
    except:
        pass
            
if __name__ == '__main__':
    main()


