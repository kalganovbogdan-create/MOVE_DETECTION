import numpy as np
from pathlib import Path
from typing import Literal
import cv2 as cv 
from src import utils
import logging
import pandas as pd
import time 


class VideoReader:
    def __init__(self, output_dir:str):
        self.output_dir = output_dir

    def write(self, capture,
              backSub,
              mask,
              MIN_AREA,
              MIN_CONTOUR_AREA,
              logger,
              logger_csv,
              CLEAR_MASK_KERNEL_SHAPE,
              frame_id):

            
            if cv.countNonZero(mask) > MIN_AREA:

                date, exact_time = utils.get_time()
                path = Path(self.output_dir) / Path(date + '.mp4')
                if not path.parent.exists():
                    path.parent.mkdir(parents=True,exist_ok=True)  
                    
                W = int(capture.get(cv.CAP_PROP_FRAME_WIDTH))
                H = int(capture.get(cv.CAP_PROP_FRAME_HEIGHT))
                fourcc = cv.VideoWriter_fourcc(*'mp4v')
                fps = capture.get(cv.CAP_PROP_FPS) or 30
                writer = cv.VideoWriter(str(path), fourcc,fps, (W,H), isColor=False)


                while cv.countNonZero(mask) > MIN_AREA:
                    ret,frame=capture.read()
                    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                    if not ret or frame is None:
                        logger.log_info('The video stream was interrupted due to a server-side error')
                        break
                    fgMask = backSub.apply(frame)
                    mask = utils.clear_mask(fgMask,kernel_shape=CLEAR_MASK_KERNEL_SHAPE)
                    res = cv.bitwise_and(frame, frame, mask = mask)
                    contours, _ = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
                    boxes = []
                    for cnt in contours:
                
                        if cv.contourArea(cnt) < MIN_CONTOUR_AREA:
                            continue
                        x, y, w, h = cv.boundingRect(cnt)
                        _, timestamp = utils.get_time()
                        add_to_csv = pd.DataFrame([{'timestamp':timestamp,
                                      'frame_id':frame_id, 'bbox_x':x,
                                      'bbox_y':y,
                                      'bbox_w':w,
                                      'bbox_h':h}])
                        logger_csv.csv_write_data(add_to_csv)
                        cv.rectangle(res,(x,y),(x+w,y+h),color=(255,255,255), thickness=2)
                        cv.rectangle(res, (10, 2), (100,20), (255,255,255), -1)
                        cv.putText(res,timestamp, (15, 15), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 200, 0), 1, cv.LINE_AA)
                        writer.write(res)
                writer.release()

    
    
class VideoLogger:
    def __init__(self, output_path:str):
        '''
        if not Path(output_path).exists():
            raise ValueError(f'Invalid file path {output_path} for the "VideoLogger" class')
        '''
        self.output_path = output_path
        self.file_type = utils.define_csv_or_log(output_path)

        
        if self.file_type == 'log':
            self.logger = logging.getLogger(__name__)
            file_hundler = logging.FileHandler(self.output_path, mode = 'a', encoding='utf-8')
            formatter = logging.Formatter('{levelname} - {asctime} - {message}', style='{', datefmt='%Y-%m-%d %H:%M')
            file_hundler.setFormatter(formatter)
            self.logger.setLevel('INFO')
            file_hundler.setLevel('INFO')
            self.logger.addHandler(file_hundler)
        elif self.file_type == 'csv':
            try:
                self.df = pd.read_csv(self.output_path)
            except:
                self.df = pd.DataFrame(columns=['timestamp', 'frame_id', 'bbox_x','bbox_y','bbox_w','bbox_h'])
                self.df.to_csv('data_rtsp.csv', index=False)
            right_columns = ['timestamp', 'frame_id', 'bbox_x','bbox_y','bbox_w','bbox_h']
            if not list(self.df.columns):
                self.df_is_empty = True
            elif list(self.df.columns) != right_columns:
                self.df = pd.DataFrame(columns=['timestamp', 'frame_id', 'bbox_x','bbox_y','bbox_w','bbox_h'])
                self.df_is_empty = True
            else:
                self.df_is_empty = False
            
            pass
        else:
            raise ValueError('Invalid file extension, file extension must be csv or log')
    
    # эти методы используются для запись в файл с log расширением 
    @utils.log_check_decorator
    def log_info(self, message):
        self.logger.info(message)
    @utils.log_check_decorator
    def log_warning(self, message):
        self.logger.warning(message)
    @utils.log_check_decorator
    def log_error(self, message:str):
        self.logger.error(message)
    @utils.log_check_decorator
    def log_critical(self, message):
        self.logger.critical(message)

    @utils.csv_check_decorator
    def csv_write_data(self,data:pd.DataFrame):
        if self.df_is_empty:
            self.df = data
        else:
            if list(data.columns) == list(self.df):
                self.df = pd.concat([self.df,data], ignore_index=True)
            else:
                raise ValueError('Invalid format of written data')
        pass
    
class MotionDetector:
    def __init__(self, config:dict):
        self.config = config
        self.CLEAR_MASK_KERNEL_SHAPE = tuple(config['CLEAR_MASK_KERNEL_SHAPE'])
        self.MIN_AREA = config['MIN_AREA'] #порог чувствительности 
        self.RTSP_URL = config['RTSP_URL']
        self.VIDEO_STORAGE_PATH = config['VIDEO_STORAGE_PATH']
        self.MIN_CONTOUR_AREA = config['MIN_CONTOUR_AREA']
        self.logger = VideoLogger(config['LOGGER_PATH_TO_LOG_FILE'])
        self.logger_csv = VideoLogger(config['CSV_STORAGE_PATH'])
        self.frame_id = 0
        self.writer = VideoReader(self.VIDEO_STORAGE_PATH)
        self.release = False

    def detect(self, mode:Literal['show','write']='write'):
        self.capture = cv.VideoCapture(self.RTSP_URL, cv.CAP_FFMPEG)
        
        if not self.capture.isOpened():
            self.logger.log_error('Error connecting to the camera via RTSP URL')
            raise ValueError('Error connecting to the camera via RTSP URL')
        backSub = cv.createBackgroundSubtractorMOG2()

        while True:
            if self.release:
                self.capture.release()
                self.logger.log_warning('video stream is disabled')
                break


            ret, frame = self.capture.read()
            if not ret or frame is None:
                self.logger.log_error('The video stream was interrupted due to a server-side error')
                break
            
            fgMask = backSub.apply(frame)
            mask = utils.clear_mask(fgMask,kernel_shape=self.CLEAR_MASK_KERNEL_SHAPE)

            self.writer.write(self.capture,
                              backSub,
                              mask,
                              self.MIN_AREA,
                              self.MIN_CONTOUR_AREA,
                              self.logger,
                              self.logger_csv,
                              self.CLEAR_MASK_KERNEL_SHAPE,
                              self.frame_id)
            self.frame_id +=1
            k = cv.waitKey(0)
            if k == 27:
                self.release = True
    def IsCapOpened(self):
        return self.capture.isOpened()
    def release(self):
        if self.IsCapOpened(self):
            self.capture.release()
        else:
            self.logger.warning('can`t release capture, capture doesn`t open')
            raise ValueError('capture doesn`t open')
    def get_log_logger(self):
        return self.logger

    
                            

                


                
