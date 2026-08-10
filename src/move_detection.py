import numpy as np
import time
import functools
from pathlib import Path
from typing import Iterator

def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        st = time.perf_counter()
        value = func(*args, **kwargs)
        et = time.perf_counter()
        elapsed = et - st
        print(f'{func.__name__} took {elapsed:.4f}s')
        return value
    return wrapper 


class VideoReader:
    def __init__(self, path : Path):
        self.path  = path
    @log_time
    def read_frame(self) -> np.ndarray:
        """Read next frame from video. Returns None if stream ended."""
        pass
    def release(self):
        """Release video capture resources."""
        pass
    #для контекстного менеджера with:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
    


def frame_generator(path : Path) -> Iterator[np.ndarray]:
    with VideoReader(path) as f:
        while True:
                frame = f.read_frame()
                if frame is None:
                    break
                yield frame
