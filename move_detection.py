import numpy as np
import time
import functools
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


class VideoReader():
    def __init__(self, path):
        self.path  = path
    @log_time
    def read_frame(self) -> np.ndarray:
        """Read next frame from video. Returns None if stream ended."""
        pass
    def release(self):
        """Release video capture resources."""
        pass


def frame_generator(path):
    with VideoReader(path)as f:
        while True:
            try:
                yield f.read_frame()
            except StopIteration:
                break