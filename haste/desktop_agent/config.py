WAIT_AFTER_FIRST_MODIFIED_SECONDS = 1
LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
LOGGING_FORMAT_AGENT = '%(asctime)s - AGENT - %(threadName)s - %(levelname)s - %(message)s'


MODE_SPLINES = 0
MODE_NATURAL = 1
MODE_GOLDEN = 2


FAKE_UPLOAD = True
FAKE_UPLOAD_SPEED_BITS_PER_SECOND = 25 * 10**6

if FAKE_UPLOAD:
    MAX_CONCURRENT_XFERS = 1
else:
    MAX_CONCURRENT_XFERS = 15 # frequency is 20, so that minus the max number of threads.


# FOR BENCHMARKING / SIMULATOR


# SOURCE_DIR = '/Users/benblamey/projects/haste/images/dummy_files/empty_files/'
# EXTENSION = '.txt'
# QUIT_AFTER = 1024

SOURCE_DIR = '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/'
EXTENSION = '.png'
QUIT_AFTER = 200#759#759#759#200#759

TARGET_DIR = '/Users/benblamey/projects/haste/haste-desktop-agent-images/target/'
FREQUENCY = 20  # looking at the filenames, 2019_02_04__11_34_55_vironova looks like 20Hz
DELETE = True

