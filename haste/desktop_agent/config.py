WAIT_AFTER_FIRST_MODIFIED_SECONDS = 1
LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
LOGGING_FORMAT_AGENT = '%(asctime)s - AGENT - %(threadName)s - %(levelname)s - %(message)s'

MODE_SPLINES = 0 # Upload the files in the order they arrive.
MODE_NATURAL = 1 # Upload the files in the order they arrive.
MODE_GOLDEN = 2

# For debugging, we can 'fake' the upload to exclude the possibility of issues relating to upload bandwidth limiting, or to allow us to benchamrk
FAKE_UPLOAD = False
FAKE_UPLOAD_SPEED_BITS_PER_SECOND = 25 * 10**6

if FAKE_UPLOAD:
    MAX_CONCURRENT_XFERS = 1 # Send one at a time, according to the fake rate.
else:
    MAX_CONCURRENT_XFERS = 15 # frequency is 20, so that minus the max number of threads.

# Command invoked for pre-processing
PREPROCESSOR_CMD = 'python3 -m haste.desktop_agent.preprocessor'
DELETE_FILE_AFTER_SENDING = True
