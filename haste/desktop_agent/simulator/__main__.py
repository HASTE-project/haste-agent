import sys
import time
import os
import shutil
import logging

import haste.desktop_agent.benchmarking.benchmarking_config
from haste.desktop_agent import config
from haste.desktop_agent.benchmarking.benchmarking_config import TARGET_DIR, EXTENSION, FREQUENCY

# Basic microscope simulator. Copies files from one dir to another at a specified frequency to simulate image capture.

if __name__ == '__main__':
    SOURCE_DIR = sys.argv[1]

    LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
    LOGGING_FORMAT = '%(asctime)s - SIMULATOR - %(threadName)s - %(levelname)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=LOGGING_FORMAT,
                        datefmt=LOGGING_FORMAT_DATE)

    logging.info('deleting all files in target dir...')

    for file_to_delete in os.listdir(TARGET_DIR):
        os.remove(TARGET_DIR + file_to_delete)

    logging.info('done... about to start stream...')

    filenames = os.listdir(SOURCE_DIR)

    filenames = filter(lambda filename: filename.endswith(EXTENSION), filenames)

    filenames = list(sorted(filenames))
    filenames = filenames[:haste.desktop_agent.benchmarking.benchmarking_config.QUIT_AFTER]

    assert len(filenames) == haste.desktop_agent.benchmarking.benchmarking_config.QUIT_AFTER

    logging.info(f'about to stream {len(filenames)} files.')

    time.sleep(10)

    for filename in filenames:
        time_last_copy_initiated = time.time()

        shutil.copyfile(SOURCE_DIR + filename, TARGET_DIR + filename + '.tmp')
        shutil.move(TARGET_DIR + filename + '.tmp', TARGET_DIR + filename)
        logging.info(f'copied file {filename}')

        pause = time_last_copy_initiated + 1 / FREQUENCY - time.time()

        if pause < 0:
            logging.warning(f'overran by {pause} seconds')
        else:
            time.sleep(pause)
