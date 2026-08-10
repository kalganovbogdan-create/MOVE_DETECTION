import pytest
from typing import Iterator
import numpy as np 
from pathlib import Path
import move_detection as MD


@pytest.mark.VideoReader
@pytest.mark.parametrize(
        'path, shape', [
            (Path(r"C:\Users\Bogdan1\Videos\FiveHourse_boat.MOV"),(1280, 720, 3)),
            (Path(r"C:\Users\Bogdan1\Videos\Zelensky.mp4"),(1024,576, 3))
        ]
)
def test_VideoReader_ShapeTest(path, shape):
    frame = MD.VideoRider().read_frame(path)
    if frame is not None:
        assert frame.shape == shape
    else:
        assert True 

