import cv2
import matplotlib
matplotlib.use('Agg') # headless backend, no display needed
import matplotlib.pyplot as plt 
import numpy as np
from pathlib import Path


def plot_detection_result(image:np.ndarray, boxes:list[list[float]], labels:list[str],save_path:Path) -> None:
    '''
    boxes have format: [[x, y, w, h], ...], where:
    x, y - coordinates of the left upper corner
    w, h - the width and height of the box respectively
    '''
    img = image.copy()
    for box, label in zip(boxes,labels):
        x, y, w, h = box

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(img, label, (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 5)
    plt.figure(figsize=(20,15))
    plt.imshow(img[:,:,::-1])
    plt.savefig(save_path)

    plt.close()