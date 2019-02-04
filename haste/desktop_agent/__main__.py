import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import aiohttp
import asyncio
import logging
import argparse
from datetime import datetime as dt

import datetime

# -u for unbuffered stdout (some issues with async code/autoflushing)
LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
ARG_PARSE_PROG_NAME = 'python3 -u -m haste.desktop-agent'

WAIT_AFTER_MODIFIED_SECONDS = 1

# TODO: store timestamps also and clear the old ones
ALREADY_WRITTEN_FILES = set()


def create_stream_id():
    stream_id = datetime.datetime.today().strftime('%Y_%m_%d__%H_%M_%S') + '_' + stream_id_tag
    return stream_id


async def post_file(filename):
    auth = aiohttp.BasicAuth(login=username, password=password)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            extra_headers = {'X-HASTE-original_filename': filename,
                             'X-HASTE-tag': stream_id_tag,
                             'X-HASTE-unixtime': str(time.time())}

            async with session.post(f'http://{host}/stream/{stream_id}',
                                    data=open(filename, 'rb'),
                                    headers=extra_headers) as response:
                logging.info(f'HASTE Response: {response.status}')
                return await response.text()

        except Exception as ex:
            logging.error(f'Exception sending file: {ex}')


async def handle(event):
    logging.debug(f'handling event: {event}')

    if event.is_directory:
        logging.debug(f'skipping directory: {event.src_path}')
        return

    src_path = event.src_path
    if (dot_and_extension is not None) and (not src_path.endswith(dot_and_extension)):
        logging.info(f'Ignoring file because of extension: {event}')
        return

    # Assuming single-thread!
    if src_path in ALREADY_WRITTEN_FILES:
        logging.info(f'File already sent: {src_path}')
        return

    ALREADY_WRITTEN_FILES.add(src_path)

    # Wait for any subsequent modifications to the file.
    # TODO: instead, poll the last modified time incase the file is modified again

    await asyncio.sleep(WAIT_AFTER_MODIFIED_SECONDS)

    logging.info(f'Sending file: {src_path}')

    return await post_file(src_path)

    logging.debug(f'Server response body: {post_response_text}')


def handle_and_log_response(event):
    response = asyncio.run(handle(event))
    logging.debug(f'response: {response}')


class HasteHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        """Catch-all event handler.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """
        logging.debug(f'on_any_event {event}')

    def on_modified(self, event):
        """Called when a file or directory is modified.

        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """

        # Under MacOSX -- doesn't seem to catch 'echo 'foo' > test-tmp/inner/foo5.txt'

        handle_and_log_response(event)

    def on_created(self, event):
        """Called when a file or directory is modified.

        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """

        handle_and_log_response(event)


logging.basicConfig(level=logging.DEBUG,
                    format=LOGGING_FORMAT,
                    datefmt=LOGGING_FORMAT_DATE)

logging.info(f'current directory is :{os.getcwd()}')
logging.debug(f'command line args arg :{sys.argv}')

parser = argparse.ArgumentParser(description='Watch directory and stream new files to HASTE', prog=ARG_PARSE_PROG_NAME)
parser.add_argument('path', metavar='path', type=str, nargs=1, help='path to watch (e.g. C:/docs/foo')
parser.add_argument('--include', type=str, nargs='?', help='include only files with this extension')
parser.add_argument('--tag', type=str, nargs='?', help='short ASCII tag to identify this machine (e.g. ben-laptop)')
parser.add_argument('--host', type=str, nargs='?', help='Hostname for HASTE e.g. foo.haste.com:80')
parser.add_argument('--username', type=str, nargs='?', help='Username for HASTE')
parser.add_argument('--password', type=str, nargs='?', help='Password for HASTE')

args = parser.parse_args()

path = args.path[0]

dot_and_extension = args.include
if dot_and_extension is not None and not dot_and_extension.startswith('.'):
    dot_and_extension = '.' + dot_and_extension

stream_id_tag = args.tag

username = args.username
password = args.password
host = args.host

# TODO: generate new stream_id after long pause in new images?
stream_id = create_stream_id()

# Now we have the stream ID, create a log file for this stream:
file_logger = logging.FileHandler(os.path.join('logs', f'log_{stream_id}.log'))
file_logger.setLevel(logging.DEBUG)
file_logger.setFormatter(logging.Formatter(LOGGING_FORMAT, LOGGING_FORMAT_DATE))
logging.getLogger('').addHandler(file_logger)

logging.info(f'stream_id: {stream_id}')

event_handler = HasteHandler()

observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

logging.info(f'began watching {path}')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
