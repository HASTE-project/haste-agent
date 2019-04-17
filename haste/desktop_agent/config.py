WAIT_AFTER_FIRST_MODIFIED_SECONDS = 1
MAX_CONCURRENT_XFERS = 20
LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
LOGGING_FORMAT_AGENT = '%(asctime)s - AGENT - %(threadName)s - %(levelname)s - %(message)s'



# FOR BENCHMARKING / SIMULATOR


# SOURCE_DIR = '/Users/benblamey/projects/haste/images/dummy_files/empty_files/'
# EXTENSION = '.txt'
# QUIT_AFTER = 1024

SOURCE_DIR = '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/'
EXTENSION = '.png'
QUIT_AFTER = 759#759#759#200#759

TARGET_DIR = '/Users/benblamey/projects/haste/haste-desktop-agent-images/target/'
FREQUENCY = 20  # looking at the filenames, 2019_02_04__11_34_55_vironova looks like 20Hz
DELETE = True