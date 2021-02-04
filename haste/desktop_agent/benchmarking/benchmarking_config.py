# from haste.desktop_agent.config import _BASE_DIR

# This file needs to be modified as per the README.md

# This is the directory for the original images, as downloaded from https://doi.org/10.17044/scilifelab.12771614.v1.
import os

# Base working directory:
_BASE_DIR = os.path.expanduser('~/haste_agent_benchmarking_images')
#_BASE_DIR = '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen'

ORIGINAL_DIR = f'{_BASE_DIR}/orig/'

# This is the directory for the identical images, correctly encoded as greyscale, which we generate:
GREYSCALE_DIR = f'{_BASE_DIR}/greyscale/'

# This is the directory for the same images with the flood-fill applied offline, used as one of the baselines:
FFILL_DIR = f'{_BASE_DIR}/ffill/'

# This is the directory which the agent watches for new files during benchmarking.
TARGET_DIR = f'{_BASE_DIR}/target/'

assert ORIGINAL_DIR.endswith('/')
assert GREYSCALE_DIR.endswith('/')
assert FFILL_DIR.endswith('/')
assert TARGET_DIR.endswith('/')

FREQUENCY = 20  # looking at the filenames, 2019_02_04__11_34_55_vironova looks like 20Hz

EXTENSION = '.png'
QUIT_AFTER = 759


HASTE_GATEWAY_PASSWORD = '???'
HASTE_GATEWAY_USERNAME = '???'
HASTE_GATEWAY_HOST = 'haste-gateway.benblamey.com:80'