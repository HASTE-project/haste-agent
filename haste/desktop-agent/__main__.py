import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, PatternMatchingEventHandler
import aiohttp
import asyncio
import logging
# import requests
from requests_futures.sessions import FuturesSession
import datetime

WAIT_AFTER_MODIFIED_SECONDS = 1

WRITTEN_FILES = set()

def create_stream_id():
    stream_id = datetime.datetime.today().strftime('%Y_%m_%d__%H_%M_%S') + '_' + stream_id_tag
    return stream_id

#

# def get_file_bytes(filename):
#     with open(filename, "rb") as f:
#         # get all bytes
#         # (ideally, would stream, but files ~1-2MB.
#         return f.read()


async def post_file(filename):

    async with aiohttp.ClientSession() as session:
        try:
            extra_headers = {'original_filename': filename}

            async with session.post(f'http://haste-gateway.benblamey.com:8888/{stream_id}/',
                                    data=open(filename, 'rb'),
                                    headers=extra_headers) as response:
                return await response.text()
        except Exception as ex:
            logging.error(f'Exception sending file: {ex}')


# async def main():
#         html = await fetch(session, 'http://python.org')
#         print(html)


# async def post(data):
#     requests.post('http://haste-gateway.benblamey.com', 'foo')


async def handle(event):
    logging.debug(f'handling event: {event}')

    if event.is_directory:
        logging.debug(f'skipping directory: {event.src_path}')
        return

    src_path = event.src_path
    if dot_and_extension is not None and not src_path.endswith(dot_and_extension):
        logging.info(f'Ignoring file because of extension: {event}')

    # Assuming single-thread!
    if src_path in WRITTEN_FILES:
        logging.info(f'File already sent: {src_path}')
        return

    WRITTEN_FILES.add(src_path)

    # Wait for any subsequent modifications to the file.
    # TODO: instead, poll the last modified time incase the file is modified again
    try:
        await asyncio.sleep(WAIT_AFTER_MODIFIED_SECONDS)
    except:
        print('--excepto--')


    logging.info(f'Sending file: {src_path}')

    # loop = asyncio.get_event_loop()
    # future1 = loop.run_in_executor(None, requests.post, 'http://haste-gateway.benblamey.com', 'foo')
    # # future2 = loop.run_in_executor(None, requests.get, 'http://www.google.co.uk')
    # response1 = await future1
    # # response2 = await future2
    # logging.debug(response1.text)
    # # print(response2.text)




    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(fetch('foo'))
    post = post_file(src_path)
    await post

    print('foo')




    # task = asyncio.create_task(post('foo'))
    # await task
    #
    # logging.info(f' exception: {task.exception()}')
    # logging.info(f' result: {task.result()}')

    # future1 = loop.run_in_executor()
    # # future2 = loop.run_in_executor(None, requests.get, 'http://www.google.co.uk')
    # response1 = await future1
    # # response2 = await future2
    # logging.debug(response1.text)
    # # print(response2.text)


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

        asyncio.run(handle(event))

    def on_created(self, event):
        """Called when a file or directory is modified.

        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """

        asyncio.run(handle(event))


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logging.info(f'current directory is :{os.getcwd()}')
logging.info(f'command line args arg :{sys.argv}')

path = sys.argv[1] if len(sys.argv) > 1 else '.'
dot_and_extension = sys.argv[2] if len(sys.argv) > 2 else None
stream_id_tag = sys.argv[3] if len(sys.argv) > 3 else 'default_tag'

stream_id = create_stream_id()

if dot_and_extension is not None and not dot_and_extension.startswith('.'):
    dot_and_extension = '.' + dot_and_extension

# event_handler = LoggingEventHandler()
event_handler = HasteHandler()

observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
