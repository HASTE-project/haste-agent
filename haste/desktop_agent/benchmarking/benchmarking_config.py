# from haste.desktop_agent.config import _BASE_DIR

# Settings for running the benchmarking -- generation of plots etc. is done in results_analysis_*
# This file needs to be modified as per the README.md


import os

# Base working directory:
_BASE_DIR = os.path.expanduser('~/Documents/_RESEARCH_AND_LEARNING/p-message-size-aware/code-message-size-aware/2019_02_04__11_34_55_vironova/all/gen')

# Images downloaded from https://doi.org/10.17044/scilifelab.12771614.v1.
ORIGINAL_DIR = f'{_BASE_DIR}/orig/'

# This is the directory for the identical images, re-saved as greyscale, which we generate:
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
HASTE_GATEWAY_HOST = 'localhost:80'
