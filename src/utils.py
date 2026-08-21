import cv2 as cv 
import numpy as np
from pathlib import Path
import functools
import time

def clear_mask(mask, kernel_shape):# kernel_shape лежит в config.yaml под названием CLEAR_MASK_KERNEL_SHAPE в виде 
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, kernel_shape)
    cm = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
    cm = cv.morphologyEx(cm,cv.MORPH_CLOSE,kernel)
    return cm

def define_csv_or_log(path:str):
    '''
    'define_csv_or_log' function determines the file extension log or csv, otherwise returns None
    '''
    npath = Path(path)
    if npath.suffix == '.csv':
        return 'csv'
    elif npath.suffix == '.log':
        return 'log'
    else:
        return None


def log_check_decorator(func):
        '''
        a decorator that checks that a class method is used for the 'log' file type  
        '''
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            if not self.file_type == 'log':
                raise ValueError(f'There is no such method for a file with the {self.file_type} extension.')
            value = func(*args, **kwargs)
            return value
        return wrapper


def csv_check_decorator(func):
        '''
        a decorator that checks that a class method is used for the 'csv' file type  
        '''
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            if not self.file_type == 'csv':
                raise ValueError(f'There is no such method for a file with the {self.file_type} extension.')
            value = func(*args, **kwargs)
            return value
        return wrapper

def write_detection_result(frame, display_name, time):
    pass


def get_time():
    t = time.localtime()
    exact_time = time.strftime("%Y-%m-%d %H-%M-%S",t)
    date = time.strftime("%Y-%m-%d",t)
    return date, exact_time

