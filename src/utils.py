import cv2 as cv 
import numpy as np
from pathlib import Path
import functools
import time
import logging
import pandas as pd


#________________________________________________________________________________________________________________________

#for VideoDetector

def clear_mask(mask, kernel_shape):# kernel_shape лежит в config.yaml под названием CLEAR_MASK_KERNEL_SHAPE в виде 
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, kernel_shape)
    cm = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
    cm = cv.morphologyEx(cm,cv.MORPH_CLOSE,kernel)
    return cm
def get_bboxes(mask, MIN_CONTOUR_AREA):
    bboxes = []
    contours, _ = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv.contourArea(cnt) < MIN_CONTOUR_AREA:
            continue
        x, y, w, h = cv.boundingRect(cnt)
        bboxes.append((x,y,w,h))
    return bboxes
def draw_bboxes(frame, bboxes, color = (0,255,0)):
    if bboxes is None:
        return
    for bbox in bboxes:
        x, y, w, h = bbox 
        if (x,y,w,h) == (0,0,0,0) or frame is None:
            return
        cv.rectangle(frame,(x,y), (x+w, y+h),color=color,thickness=2)
    
         
#________________________________________________________________________________________________________________________

#for VideoLogger
def LogLogger(LOG_PATH:str):
    formatter = logging.Formatter('{levelname} - {asctime} - {message}',
                                  style='{',
                                  datefmt='%Y-%m-%d %H:%M:%S',)
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel('INFO')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(LOG_PATH,mode='a',encoding='utf-8')
        file_handler.setLevel('DEBUG')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
    
class CSVLogger:
    def __init__(self,  CSV_PATH:str, logger):
        self.CSV_PATH = CSV_PATH
        self.logger = logger
        self.cols = ['frame_id','motion_id','timestamp','bx','by','bw','bh']
        if not Path(self.CSV_PATH).exists():
            self.df = pd.DataFrame(columns=self.cols)
            self.df.to_csv(CSV_PATH, index=False)
        else:
            try:
                self.df = pd.read_csv(self.CSV_PATH)
            except:
                raise ValueError('ошибка при открытии CSV_PATH')
            if list(self.df.columns) != self.cols:
                raise ValueError('неверный формат CSV файла, неправильные колонки ')

    def write(self, frame_id:int, motion_id:int, timestamp:float, bboxes:list[tuple]):
        if not bboxes:
            bboxes = [(0,0,0,0)]
        new_data = []
        for i in range(len(bboxes)):
            if len(bboxes[i]) != 4:
                bboxes[i] = ('None','None','None','None')
            new_data.append([frame_id,motion_id,timestamp,*bboxes[i]])
        new_data = pd.DataFrame(new_data, columns=self.cols)
        self.df = pd.concat([self.df, new_data],ignore_index=True)
    def save(self):
        self.logger.info('сохраняем данные в csv_file')
        self.df.to_csv(self.CSV_PATH, index=False)
    
#________________________________________________________________________________________________________________________
# for VideoReader

def reread(capture, num_try):
    for _ in range(num_try):
        ret,frame = capture.read()
        if frame is not None:
            return True
    return False

def release_config(config):
    config['RElEASE'] = True


##-----------------------------------------------------

