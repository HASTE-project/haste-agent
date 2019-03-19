import queue
import time
from watchdog.observers import Observer
import asyncio
import logging
import ben_images.file_utils

from haste.desktop_agent.FSEvents import HasteFSEventHandler
from haste.desktop_agent.args import initialize
from haste.desktop_agent.config import MAX_CONCURRENT_XFERS
from haste.desktop_agent.http import send_file

# TODO: store timestamps also and clear the old ones
already_written_files = set()
events_to_process = []

path, dot_and_extension, stream_id_tag, username, password, host, stream_id = initialize()


def put_event_on_queue(event):
    # Called on a worker thread. Put an FS event on the thread-safe queue.

    if event.is_directory:
        logging.debug(f'skipping directory: {event.src_path}')
        return

    src_path = event.src_path
    if (dot_and_extension is not None) and (not src_path.endswith(dot_and_extension)):
        logging.info(f'Ignoring file because of extension: {event}')
        return

    # There is no race here, because we're only using a single thread.

    # Since, Set is a hashset, this is O(1)
    if src_path in already_written_files:
        logging.info(f'File already sent: {src_path}')
        return

    already_written_files.add(src_path)

    event.timestamp = time.time()

    # Queue never full, has infinite capacity.
    events_to_process_mt_queue.put(event, block=True)
    logging.info(f'on_created() -- pushed event: {event}')


async def xfer_events(name):
    # Async on the main thread. Xfer events from the thread-safe queue onto the async queue on the main thread.
    logging.debug(f'{name} started')

    while True:
        try:
            event = events_to_process_mt_queue.get_nowait()
            event.file_size = ben_images.file_utils.get_file_size(event.src_path)
            events_to_process.append(event)

            # The first files in the list will be sent first.
            heuristics = [
                # Send the oldest files first (FIFO):
                lambda: events_to_process.sort(key=event.file_size, reverse=False),
                # Send the newest files first (LIFO):
                lambda: events_to_process.sort(key=event.file_size, reverse=True),
            ]

            heuristics[0]()

            await events_to_process_async_queue.put(object())
        except queue.Empty:
            await asyncio.sleep(0.1)


async def worker(name, queue):
    # Process events from the queue on the main thread.
    logging.debug(f'Worker {name} started')

    try:
        while True:
            await queue.get()

            file_system_event = events_to_process.pop(0)

            logging.debug(f'event {file_system_event} popped from queue')
            response = await send_file(file_system_event, stream_id_tag, stream_id, username, password, host)
            logging.debug(f'Server response body: {response}')
            queue.task_done()
    except Exception as ex:
        logging.error(f'Exception on {name}: {ex}')


async def main():
    # -u for unbuffered stdout (some issues with async code/autoflushing)

    global events_to_process_mt_queue, events_to_process_async_queue

    events_to_process_mt_queue = queue.Queue()  # thread safe queue, no async support.
    events_to_process_async_queue = asyncio.Queue()  # async Queue, not thread safe

    observer = Observer()
    event_handler = HasteFSEventHandler(put_event_on_queue)
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # Create workers to process events from the queue.
    # Here, there is a single worker thread.
    tasks = []

    task = asyncio.create_task(xfer_events(f'events-xfer'))
    tasks.append(task)

    for i in range(MAX_CONCURRENT_XFERS):
        task = asyncio.create_task(worker(f'worker-{i}', events_to_process_async_queue))
        tasks.append(task)

    logging.info(f'began watching {path}')

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        await asyncio.gather(*tasks, return_exceptions=True)

    observer.join()


asyncio.run(main())
