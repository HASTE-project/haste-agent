import time
import os
import shutil
import logging

SOURCE_DIR = '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/'
EXTENSION = '.png'

# SOURCE_DIR = '/Users/benblamey/projects/haste/images/dummy_files/empty_files/'
# EXTENSION = '.txt'


TARGET_DIR = '/Users/benblamey/projects/haste/haste-desktop-agent-images/target/'
FREQUENCY = 10  # looking at the filenames, 2019_02_04__11_34_55_vironova looks like 20Hz

if __name__ == '__main__':
    LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
    LOGGING_FORMAT = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=LOGGING_FORMAT,
                        datefmt=LOGGING_FORMAT_DATE)

    logging.info('deleting all files in target dir...')

    for file_to_delete in os.listdir(TARGET_DIR):
        os.remove(TARGET_DIR + file_to_delete)

    logging.info('done... about to start stream...')
    time.sleep(5)

    filenames = os.listdir(SOURCE_DIR)

    filenames = filter(lambda filename: filename.endswith(EXTENSION), filenames)

    filenames = list(sorted(filenames))

    for filename in filenames:
        time_last_copy_initiated = time.time()

        shutil.copyfile(SOURCE_DIR + filename, TARGET_DIR + filename + '.tmp')
        shutil.move(TARGET_DIR + filename + '.tmp', TARGET_DIR + filename)
        logging.info(f'copied file {filename}')

        pause = time_last_copy_initiated + 1 / FREQUENCY - time.time()

        if pause < 0:
            logging.warn(f'overran by {pause} seconds')
        else:
            time.sleep(pause)
