import numpy as np
from pathlib import Path
from typing import Literal
import cv2 as cv 
from src import utils
import logging
import pandas as pd
import time 

#______________________________________________________________________________________________________________________________________________
class VideoLogger:
    def __init__(self, LOG_PATH, CSV_PATH, VIDEO_PATH):
        self.logger = utils.LogLogger(LOG_PATH)
        self.csv_logger = utils.CSVLogger(CSV_PATH, self.logger)
        self.VIDEO_PATH = VIDEO_PATH
    def save_motion(self, frame_buffer:list[list], motion_id:int, fps:int, W:int,H:int):
        if not frame_buffer:
            return 
        save_path = Path(self.VIDEO_PATH) / Path(f'{motion_id}.mp4')
        if not save_path.parent.exists():
            save_path.parent.mkdir(parents=True,exist_ok=True)
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        writer = cv.VideoWriter(str(save_path),fourcc,fps,(W,H))
        
        for frame_box in frame_buffer:
            if frame_box[1] is not None:
                    writer.write(frame_box[1])
        writer.release()

#______________________________________________________________________________________________________________________________________________
class VideoReader:
    def __init__(self, logger:logging,Logger:VideoLogger, config):
        self.RTSP_URL = config['RTSP_URL']
        self.frame_id:int = 0
        self.frame_buffer:list[np.ndarray] = []
        self.motion_id:int = 0
        self.logger  = logger
        self.detector = MotionDetector(config)
        self.frame_generator = self.read()
    def start_capture(self, RTSP_URL):
        self.capture = cv.VideoCapture(RTSP_URL, cv.CAP_FFMPEG) 
        if not self.capture.isOpened():
            self.capture.release()
            raise ValueError('Не удалось подключиться к камере')
        
    def release_capture(self):
        self.capture.release()

    def read(self):
        while True:
            try:
                ret, frame = self.capture.read()
            except:
                self.logger.error('Ошибка поучения кадра')
                raise ValueError('Ошибка поучения кадра')
            
            if frame is None:
                for _ in range(5):
                    self.capture.release()
                    self.capture = cv.VideoCapture(self.RTSP_URL, cv.CAP_FFMPEG)
                    ret, frame = self.capture.read()
                    if ret:
                        break
                if not ret:
                    self.logger.error('Ошибка в чтении кадра, отключаюсь от камеры')
                    self.capture.release()
                    raise ValueError('Ошибка в чтении кадра')
            frame_id = self.frame_id
            self.frame_id+=1

            yield frame_id, frame

    
    def write_buffer(self, csv_logger:utils.CSVLogger):
        '''
        записывает кадры и мх id с камеры за 1 минуту до начала движеняи и 1 мнуту после конца движения

        '''
        
        fps = int(round(self.capture.get(cv.CAP_PROP_FPS))) or 10
        self.logger.info('начало работы write buffer')
        trigger = int(round(fps*5))

        while True:

            self.logger.info('начали записывать буффер')
            if len(self.frame_buffer) > trigger:
                N = len(self.frame_buffer)
                self.frame_buffer = self.frame_buffer[N-trigger:]
            
            while len(self.frame_buffer) < trigger:
                local_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                frame_id, frame = next(self.frame_generator)
                self.frame_buffer.append([frame_id, frame])
                cv.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
                cv.putText(frame, f'time={local_time}', (15, 15), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 200, 0), 1, cv.LINE_AA)
            self.logger.info('пераввя часть буффера готова ')


            motion_detected = False
            i = 0
            while i < trigger:
                frame_id, frame = next(self.frame_generator)
                motion_flag, timestamp, bboxes = self.detector.detect(frame)
                
                local_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))
                cv.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
                cv.putText(frame, f'time={local_time}', (15, 15), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 200, 0), 1, cv.LINE_AA)
                self.frame_buffer.append([frame_id, frame])
                i+=1
                if motion_flag:
                    self.logger.info('движение замечано motion_flag == True')
                    utils.draw_bboxes(frame,bboxes)
                    csv_logger.write(frame_id,self.motion_id,timestamp,bboxes)
                    motion_detected = True
                    i=0
            self.logger.info('закончили записывать буффер')
            csv_logger.save()
            self.logger.info('численные значения сохранены в csv file')
            if not motion_detected:
                self.logger.info('движение не произошло, возвращаем пустой буффер')
                yield [], self.motion_id
            else:
                self.logger.info('движение произошло, возвращаем буффер с кадрами')
                self.motion_id += 1
                yield self.frame_buffer, self.motion_id
            
            
#______________________________________________________________________________________________________________________________________________
class MotionDetector:

    def __init__(self, config:dict):
        self.CLEAR_MASK_KERNEL_SHAPE=config['CLEAR_MASK_KERNEL_SHAPE']
        self.MIN_AREA=config['MIN_AREA']
        self.MIN_CONTOUR_AREA=config['MIN_CONTOUR_AREA']
        self.backSub = cv.createBackgroundSubtractorMOG2()
        self.frame_buffer:list[np.ndarray] = []#для записи 1 до начала движения и 1 минту после конца движения 
    def detect(self, frame: np.ndarray): 
        '''
        возвращает:
        detect_flag:bool - True если было замечано движение False елси нет
        timestamp:float - время в секундах 
        bboxes:list[tuple] - [(x,y,w,h),...] - координаты и размеры bbox-ов, если движение не замечано, то None  
        '''
        mask = utils.clear_mask(self.backSub.apply(frame), kernel_shape=self.CLEAR_MASK_KERNEL_SHAPE)
        timestamp = time.time()
        if cv.countNonZero(mask) < self.MIN_AREA:
            return False, timestamp, None
        bboxes = utils.get_bboxes(mask,self.MIN_CONTOUR_AREA)
        return True, timestamp, bboxes
        

        
    
                            

                


                
