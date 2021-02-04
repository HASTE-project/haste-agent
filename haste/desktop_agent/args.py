import argparse
import datetime
import logging
import os
import sys

from haste.desktop_agent.config import LOGGING_FORMAT_AGENT, LOGGING_FORMAT_DATE
from haste.desktop_agent.benchmarking.benchmarking_config import FREQUENCY


def parse_args():
    parser = argparse.ArgumentParser(description='Watch directory and stream new files to HASTE',
                                     prog=ARG_PARSE_PROG_NAME)

    parser.add_argument('path', metavar='path', type=str, nargs=1, help='path to watch (e.g. C:/docs/foo')
    parser.add_argument('--include', type=str, nargs='?', help='include only files with this extension')
    parser.add_argument('--tag', type=str, nargs='?', help='short ASCII tag to identify this machine (e.g. ben-laptop)')
    parser.add_argument('--host', type=str, nargs='?', help='Hostname for HASTE e.g. foo.haste.com:80')
    parser.add_argument('--username', type=str, nargs='?', help='Username for HASTE')
    parser.add_argument('--password', type=str, nargs='?', help='Password for HASTE')

    parser.add_argument('--x-preprocessing-cores', default=1, type=int)
    parser.add_argument('--x-mode', default=1, type=int)
    parser.set_defaults(prio=True)

    args = parser.parse_args()
    return args


ARG_PARSE_PROG_NAME = 'python3 -u -m haste.desktop-agent'


def create_stream_id(stream_id_tag):
    stream_id = datetime.datetime.today().strftime('%Y_%m_%d__%H_%M_%S') + '_' + stream_id_tag
    return stream_id


def initialize():
    logging.basicConfig(level=logging.INFO,
                        format=LOGGING_FORMAT_AGENT,
                        datefmt=LOGGING_FORMAT_DATE)

    args = parse_args()
    path = args.path[0]

    dot_and_extension = args.include
    if dot_and_extension is not None and not dot_and_extension.startswith('.'):
        dot_and_extension = '.' + dot_and_extension

    stream_id_tag = args.tag
    username = args.username
    password = args.password
    host = args.host

    x_preprocessing_cores = args.x_preprocessing_cores
    x_mode = args.x_mode

    # TODO: generate new stream_id after long pause in new images?

    stream_id = create_stream_id(stream_id_tag)

    logging.info(f'current directory is: {os.getcwd()}')
    # Now we have the stream ID, create a log file for this stream:

    file_logger = logging.FileHandler(os.path.join('logs', f'agent_log_{stream_id}.log'))
    file_logger.setLevel(logging.INFO)
    file_logger.setFormatter(logging.Formatter(LOGGING_FORMAT_AGENT, LOGGING_FORMAT_DATE))

    logging.getLogger('').addHandler(file_logger)

    logging.getLogger('').addHandler(logging.StreamHandler())

    logging.debug(f'command line args arg: {sys.argv}')
    logging.info(f'stream_id: {stream_id}')

    logging.info(f'x_mode: {x_mode}')
    logging.info(f'preprocessing_cores: {x_preprocessing_cores}')

    logging.info(f'simulator_frequency (incase simulator used): {FREQUENCY}')

    logging.debug(f'command line args arg: {sys.argv}')

    return path, dot_and_extension, stream_id_tag, username, password, host, stream_id, x_preprocessing_cores, x_mode
