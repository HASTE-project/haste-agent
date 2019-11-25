import datetime
import logging
import os
import sys
import ben_images.flood_fill
from PIL import Image
import numpy as np
import time
from sys import stdin

from haste.desktop_agent.config import LOGGING_FORMAT_DATE, LOGGING_FORMAT_AGENT

# NOTE: THE PRE-PROCESSING IS RUN FROM ANOTHER MODULE


def convert_file(input_filepath, output_filepath):
    img = Image.open(input_filepath)
    im_array1 = np.asarray(img)

    result = ben_images.flood_fill.flood_fill_outer(im_array1)

    # to greyscale
    Image.fromarray(result).convert('L').save(output_filepath, format='PNG')

    return output_filepath


if __name__ == '__main__':

    if False:
        id = datetime.datetime.today().strftime('%Y_%m_%d__%H_%M_%S') + ' ' + str(os.getpid())

        file_logger = logging.FileHandler(os.path.join('logs', f'prepro_log_{id}.log'))
        file_logger.setLevel(logging.INFO)
        file_logger.setFormatter(logging.Formatter(LOGGING_FORMAT_AGENT, LOGGING_FORMAT_DATE))
        logging.getLogger('').addHandler(file_logger)

    try:
        while True:
            start_waiting = time.time()
            input_filepath, output_filepath = input().split(',')
            done_waiting = time.time()

            start = time.time()

            convert_file(input_filepath, output_filepath)

            print(str(time.time() - start) + ',' + str(done_waiting - start_waiting))
    except EOFError:
        # parent died. die
        pass
