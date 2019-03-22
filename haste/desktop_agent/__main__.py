import queue
import time
from types import SimpleNamespace

from haste.desktop_agent.golden import get_golden_prio_for_filename
from watchdog.observers import Observer
import asyncio
import logging
import ben_images.file_utils
from haste.desktop_agent.FSEvents import HasteFSEventHandler
from haste.desktop_agent.args import initialize
from haste.desktop_agent.config import MAX_CONCURRENT_XFERS
from haste.desktop_agent.benhttp import send_file

# TODO: store timestamps also and clear the old ones
already_written_files = set()
files_to_send = []
needs_sorting = False
timestamp_first_event = -1

stats_total_bytes_sent = 0
stats_preprocessed_files_sent = 0
stats_not_preprocessed_files_sent = 0

path, dot_and_extension, stream_id_tag, username, password, host, stream_id = initialize()


def put_event_on_queue(event):
    global timestamp_first_event
    # Called on a worker thread. Put an FS event on the thread-safe queue.

    if event.is_directory:
        logging.debug(f'skipping directory: {event.src_path}')
        return

    src_path = event.src_path
    if (dot_and_extension is not None) and (not src_path.endswith(dot_and_extension)):
        logging.info(f'Ignoring file because of extension: {event}')
        return

    # Set is a hashset, this is O(1)
    if src_path in already_written_files:
        logging.info(f'File already sent: {src_path}')
        return

    already_written_files.add(src_path)

    event.timestamp = time.time()
    if timestamp_first_event < 0:
        timestamp_first_event = event.timestamp

    event.golden_bytes_reduction = get_golden_prio_for_filename(src_path.split('/')[-1])
    event.preprocessed = False

    # Queue never full, has infinite capacity.
    events_to_process_mt_queue.put(event, block=True)
    logging.info(f'on_created() -- pushed event: {event}')


async def xfer_events_from_fs(name):
    # Async on the main thread. Xfer events from the thread-safe queue onto the async queue on the main thread.
    logging.debug(f'{name} started')

    while True:
        try:
            event = events_to_process_mt_queue.get_nowait()
            await push_event(event)
        except queue.Empty:
            await asyncio.sleep(0.01)


async def preprocess_async_loop(name, queue):
    count = 0
    try:
        proc = await asyncio.create_subprocess_shell(
            'python3 -m haste.desktop_agent.preprocessor',
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE)

        while True:
            file_system_event = await pop_event(queue, True)

            if not file_system_event.preprocessed:
                logging.info(f'preprocessing: {file_system_event.src_path}')

                output_filepath = '/tmp/' + file_system_event.src_path.split('/')[-1]

                line_to_send = f"{file_system_event.src_path},{output_filepath}\n"

                # add to the buffer
                proc.stdin.write(line_to_send.encode())
                await proc.stdin.drain()

                stdoutline_duration = await proc.stdout.readline()
                stdoutline_duration = stdoutline_duration.decode().strip()
                logging.info(f'stdout from preprocessor: {float(stdoutline_duration)}')

                file_system_event2 = SimpleNamespace()
                file_system_event2.timestamp = time.time()
                file_system_event2.src_path = output_filepath
                file_system_event2.golden_bytes_reduction = -1
                file_system_event2.preprocessed = True

                event_to_re_add = file_system_event2

                count += 1
                logging.info(f'preprocessed {count} files')

            else:
                # We've preprocessed everything. just re-add the original event.
                event_to_re_add = file_system_event

            await push_event(event_to_re_add)
            queue.task_done()

            # We've preprocessed everything. just re-add the original event and 'sleep' a little.
            if file_system_event.preprocessed:
                await asyncio.sleep(0.01)

    except Exception as ex:
        logging.error(ex)
        raise ex


async def push_event(event_to_re_add):
    global needs_sorting
    event_to_re_add.file_size = ben_images.file_utils.get_file_size(event_to_re_add.src_path)
    files_to_send.append(event_to_re_add)
    needs_sorting = True

    log_queue_info()

    return await events_to_process_async_queue.put(object())


def log_queue_info():
    count_preprocessed = len(list(filter(lambda f: f.preprocessed, files_to_send)))
    count_not_preprocessed = len(files_to_send) - count_preprocessed
    logging.info(f'PLOT - {time.time()} - {count_preprocessed} - {count_not_preprocessed}')


async def pop_event(queue, for_preprocessing):
    global needs_sorting

    await queue.get()

    if needs_sorting:

        start = time.time()

        # "False sorts first"
        # key = lambda e: (not e.preprocessed, -e.file_size)  # preprocessed=True, then largest first
        key = lambda e: (e.preprocessed,
                         -e.golden_bytes_reduction)  # with Ground Truth. Prioritize where we know we can reduce the bytes the least. preprocessed=False
        # key = lambda e: (not e.preprocessed, e.timestamp)

        files_to_send.sort(key=key)

        # sorting took 0.0001437664031982422 secs
        # logging.info(f'sorting took {time.time() - start} secs')

        needs_sorting = False

    if for_preprocessing:
        result = files_to_send.pop(0)
    else:
        # Prioritize sending a pre-processed file, else the one with lowest prio for pre-processing.
        if files_to_send[0].preprocessed:
            result = files_to_send.pop(0)
        else:
            result = files_to_send.pop(-1)

    log_queue_info()

    return result


async def worker_send_files(name, queue):
    global stats_total_bytes_sent, stats_preprocessed_files_sent, stats_not_preprocessed_files_sent

    # Process events from the queue on the main thread.
    logging.debug(f'Worker {name} started')

    try:
        while True:
            file_system_event = await pop_event(queue, False)
            logging.debug(f'event {file_system_event} popped from queue')
            response = await send_file(file_system_event, stream_id_tag, stream_id, username, password, host)

            stats_total_bytes_sent += file_system_event.file_size
            if file_system_event.preprocessed:
                stats_preprocessed_files_sent += 1
            else:
                stats_not_preprocessed_files_sent += 1

            if len(files_to_send) == 0:
                logging.info(f'Queue_is_empty. Duration since first event: {time.time() - timestamp_first_event}')
                logging.info(
                    f'Queue_is_empty. total_bytes_sent: {stats_total_bytes_sent} preprocessed_files_sent: {stats_preprocessed_files_sent} raw_files_sent: {stats_not_preprocessed_files_sent}')

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

    task = asyncio.create_task(xfer_events_from_fs(f'events-xfer'))
    tasks.append(task)

    if False:
        task = asyncio.create_task(preprocess_async_loop(f'preprocess', events_to_process_async_queue))
        tasks.append(task)

    for i in range(MAX_CONCURRENT_XFERS):
        task = asyncio.create_task(worker_send_files(f'worker-{i}', events_to_process_async_queue))
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
