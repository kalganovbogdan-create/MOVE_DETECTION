import argparse
from pathlib import Path
import logging
logging.basicConfig(
    level = logging.INFO,
    format = '{asctime} - {levelname} - {message}',
    style = '{',
)
logger = logging.getLogger(__name__)    
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', 
        type = str,
        help ='path to the directory containing the required videos',
        required= True
    )

    parser.add_argument(
        '--output', 
        type = str,
        help ='path to the output file storage',
        required= True
    )

    parser.add_argument(
        '--size', 
        type = int,
        help ='size of the final frames',
        default = 640
    )

    namespace = parser.parse_args()
    input_path = Path(namespace.input)
    if not input_path.exists():
        raise FileNotFoundError('This path doesn`t exist')
    output_path = Path(namespace.output)
    size = namespace.size
    return input_path, output_path, size


def process_frames(video_path,output_path, size):

    """
    тут будет реализоваться логика масштабирования кадров из видео из video_path 
    и сохранения результатов в output_path
    """
    logger.info(f'{video_path} is processing')
    output_path.mkdir(parents =True, exist_ok = True)

    return 0 #возвращает количество обработанных кадров
        

def main():
    input_path, output_path, size = parse()
    video_paths = list(input_path.glob('*.mp4'))

    if video_paths:
        logger.info(f'{len(video_paths)} videos were found')
        for video_path in video_paths:
            count = process_frames(video_path, output_path, size)
            logger.info(f'{count} frames were processed and saved')
    else:
        logger.warning('No .mp4 files found, exiting')


if __name__ == '__main__':
    main()




