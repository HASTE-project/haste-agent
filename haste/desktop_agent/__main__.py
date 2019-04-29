import queue
import threading
import time
from subprocess import Popen
from types import SimpleNamespace
import os
import traceback

from haste.desktop_agent import golden
from haste.desktop_agent.golden import get_golden_prio_for_filename
from haste.desktop_agent.master_queue import MasterQueue
from watchdog.observers import Observer
import asyncio
import logging
import ben_images.file_utils
from haste.desktop_agent.FSEvents import HasteFSEventHandler
from haste.desktop_agent.args import initialize
from haste.desktop_agent.config import MAX_CONCURRENT_XFERS, QUIT_AFTER, DELETE, FAKE_UPLOAD, \
    FAKE_UPLOAD_SPEED_BITS_PER_SECOND
from haste.desktop_agent.post_file import send_file

# TODO: store timestamps also and clear the old ones
already_written_filenames = set()
# files_to_send = []
# needs_sorting = False
timestamp_first_event = -1

stats_total_bytes_sent = 0
stats_preprocessed_files_sent = 0
stats_not_preprocessed_files_sent = 0
stats_events_pushed_first_queue = 0
stats_events_pushed_second_queue_preprocessed = 0
stats_events_pushed_second_queue_raw = 0
stats_total_preproc_duration = 0

path, dot_and_extension, stream_id_tag, username, password, host, stream_id, x_preprocessing_cores, x_mode = initialize()
assert path.endswith('/')

ground_truth = golden.csv_results[0:QUIT_AFTER]
golden_estimated_scores = (ground_truth['input_file_size_bytes'] - ground_truth[
    'output_file_size_bytes']) / ground_truth['duration_total']

master_queue = MasterQueue(QUIT_AFTER, x_mode, golden_estimated_scores)

time_last_full_dir_listing = -1
TOO_LONG = 0.005


def thread_worker_poll_fs():
    global time_last_full_dir_listing

    try:
        while True:
            PAUSE = 0.5
            # There are some issues with the watchdog -- sometimes files seem to be missed.
            # As a workaround, do a full directory listing each second.
            if time_last_full_dir_listing > 0:
                pause = (time_last_full_dir_listing + PAUSE) - time.time()
                if pause > 0:
                    time.sleep(pause)
                else:
                    logging.warn(f'fs poll overran by {pause}')

            filenames = os.listdir(path)
            time_last_full_dir_listing = time.time()
            # logging.info(f'completed scan - {len(filenames)}')
            # print(f'completed scan - {len(filenames)}')

            for filename in filenames:
                if filename in already_written_filenames:
                    continue

                filenames.sort()  # timestamp at front of filename

                new_event = SimpleNamespace()
                new_event.src_path = path + filename
                new_event.is_directory = False
                put_event_on_queue(new_event)
    except Exception as ex:
        logging.error(f'exception on polling thread: {traceback.format_exc()}')


def put_event_on_queue(event):
    global timestamp_first_event, stats_events_pushed_first_queue
    # Called on a worker thread. Put an FS event on the thread-safe queue.

    if event.is_directory:
        logging.debug(f'skipping directory: {event.src_path}')
        return

    src_path = event.src_path
    if (dot_and_extension is not None) and (not src_path.endswith(dot_and_extension)):
        logging.debug(f'Ignoring file because of extension: {event}')
        return

    # Set is a hashset, this is O(1)
    if src_path.split('/')[-1] in already_written_filenames:
        logging.debug(f'File already sent: {src_path}')
        return

    already_written_filenames.add(src_path.split('/')[-1])

    event.timestamp = time.time()

    if timestamp_first_event < 0:
        timestamp_first_event = event.timestamp

    if False:
        event.golden_bytes_reduction = get_golden_prio_for_filename(src_path.split('/')[-1])

    event.preprocessed = False
    event.file_size = ben_images.file_utils.get_file_size(event.src_path)

    # Queue never full, has infinite capacity.
    events_to_process_mt_queue.put(event, block=True)

    stats_events_pushed_first_queue += 1

    logging.info(
        f'put_event_on_queue() -- pushed event: {event.src_path} -- stats_events_pushed_first_queue: {stats_events_pushed_first_queue}')


async def xfer_events_from_fs(name):
    # Async on the main thread. Xfer events from the thread-safe queue onto the async queue on the main thread.
    logging.debug(f'{name} started')

    time_after_async = 0
    try:
        while True:
            try:
                event = events_to_process_mt_queue.get_nowait()

                time_blocked = time.time() - time_after_async
                if time_blocked > TOO_LONG:
                    logging.info(f'xfer_events_from_fs spent {time_blocked} blocking main thread')

                await push_event(event)
            except queue.Empty:
                await asyncio.sleep(0.1)
            time_after_async = time.time()
    except Exception as ex:
        print(ex)


async def preprocess_async_loop(name, queue):
    global stats_total_preproc_duration
    count = 0
    try:
        proc = await asyncio.create_subprocess_shell(
            'python3 -m haste.desktop_agent.preprocessor',
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE)

        while True:
            file_system_event = await pop_event(True)

            if file_system_event is not None:
                logging.info(f'preprocessing: {file_system_event.src_path}')

                output_filepath = '/tmp/' + file_system_event.src_path.split('/')[-1]

                line_to_send = f"{file_system_event.src_path},{output_filepath}\n"

                # add to the buffer
                proc.stdin.write(line_to_send.encode())
                await proc.stdin.drain()

                stdoutline = await proc.stdout.readline()
                stdoutline = stdoutline.decode().strip()
                logging.info(f'stdout from preprocessor: {stdoutline}')

                dur_preproc = float(stdoutline.split(',')[0])
                dur_waiting = float(stdoutline.split(',')[1])

                logging.debug(f'preprocessor waiting: {dur_waiting}')

                file_system_event2 = SimpleNamespace()
                file_system_event2.timestamp = time.time()
                file_system_event2.src_path = output_filepath

                file_system_event2.file_size = ben_images.file_utils.get_file_size(output_filepath)

                file_system_event2.golden_bytes_reduction = (
                                                                    file_system_event.file_size - file_system_event2.file_size) / dur_preproc

                stats_total_preproc_duration += dur_preproc

                file_system_event2.preprocessed = True
                file_system_event2.index = file_system_event.index

                event_to_re_add = file_system_event2

                count += 1
                logging.info(f'preprocessed {count} files')

                if DELETE:
                    os.unlink(file_system_event.src_path)

            else:
                # We've preprocessed everything. just re-add the original event.
                event_to_re_add = file_system_event

            await push_event(event_to_re_add)
            queue.task_done()

            # We've preprocessed everything for now. just re-add the original event and 'sleep' a little.
            if file_system_event is None:
                await asyncio.sleep(0.2)

    except Exception as ex:
        logging.error(traceback.format_exc())
        raise ex


# def log_queue_info():
#     # Log info about the present state of the queue
#     count_preprocessed = len(list(filter(lambda f: f.preprocessed, files_to_send)))
#     count_not_preprocessed = len(files_to_send) - count_preprocessed
#     logging.info(f'PLOT - {time.time()} - {count_preprocessed} - {count_not_preprocessed}')


async def push_event(event_to_re_add):
    global needs_sorting, stats_events_pushed_second_queue_preprocessed, stats_events_pushed_second_queue_raw

    if event_to_re_add is not None:
        if event_to_re_add.preprocessed:
            stats_events_pushed_second_queue_preprocessed += 1
        else:
            stats_events_pushed_second_queue_raw += 1

        logging.info(
            f'push_event() - raw:{stats_events_pushed_second_queue_raw}')

        if event_to_re_add.preprocessed:
            master_queue.notify_file_preprocessed(event_to_re_add.index, event_to_re_add.golden_bytes_reduction,
                                                  event_to_re_add)
        else:

            master_queue.new_file(event_to_re_add)

    return await events_to_process_async_queue.put(object())


async def pop_event(for_preprocessing):
    await events_to_process_async_queue.get()

    start = time.time()
    if for_preprocessing:
        index, result = master_queue.pop_file_to_preprocess()
    else:
        index, result = master_queue.pop_file_to_send()

    logging.debug(f'popping_took: {time.time() - start}')

    if result is not None:
        result.index = index

    return result


async def worker_send_files(name, queue):
    global stats_total_bytes_sent, stats_preprocessed_files_sent, stats_not_preprocessed_files_sent

    # Process events from the queue on the main thread.
    logging.debug(f'Worker {name} started')

    last = 0

    try:
        while True:

            if time.time() - last > TOO_LONG:
                logging.info(f'worker_took: {time.time() - last}')

            file_system_event = await pop_event(False)
            logging.debug(f'event {file_system_event} popped from queue')

            # takes ~0.0003s
            # start_file_read = time.time()
            # f = open(file_system_event.src_path, 'rb')
            # filelike = f.read()
            # f.close()
            # logging.info(f'file_read_took: {time.time()-start_file_read}')

            filelike = file_system_event.src_path

            if FAKE_UPLOAD:
                # (only 1 concurrent upload)
                fake_upload_time = (file_system_event.file_size * 8) / FAKE_UPLOAD_SPEED_BITS_PER_SECOND
                logging.info(f'Fake sleep for: {fake_upload_time}')
                await asyncio.sleep(fake_upload_time)
            else:
                response = await send_file(file_system_event, filelike, stream_id_tag, stream_id, username, password,
                                           host)
                logging.debug(f'Server response body: {response}')

            last = time.time()

            if DELETE:
                start_delete = time.time()
                if False:
                    # this takes ~0.005...at ~10Hz this is too slow?
                    # close_fds makes the parent process' file handles inaccessible for the child.
                    proc = Popen(f'rm {file_system_event.src_path}', shell=True, stdin=None, stdout=None, stderr=None,
                                 close_fds=True)
                else:
                    os.unlink(file_system_event.src_path)
                logging.debug(f'starting delete took: {start_delete - time.time()}')

            stats_total_bytes_sent += file_system_event.file_size
            if file_system_event.preprocessed:
                stats_preprocessed_files_sent += 1
            else:
                stats_not_preprocessed_files_sent += 1

            queue.task_done()

            master_queue.notify_file_sent(file_system_event.index)

            logging.info(
                f'total_bytes_sent: {stats_total_bytes_sent} preprocessed_files_sent: {stats_preprocessed_files_sent} raw_files_sent: {stats_not_preprocessed_files_sent}')

            # Benchmarking hack
            if stats_not_preprocessed_files_sent + stats_preprocessed_files_sent == QUIT_AFTER:
                logging.info(
                    f'Queue_is_empty. Duration since first event: {time.time() - timestamp_first_event} - total_bytes_sent: {stats_total_bytes_sent} preprocessed_files_sent: {stats_preprocessed_files_sent} raw_files_sent: {stats_not_preprocessed_files_sent} stats_total_preproc_duration: {stats_total_preproc_duration}')
                # master_queue.plot()
                quit()

    except Exception as ex:
        logging.error(f'Exception on {name}: {traceback.format_exc()}')
        print(ex)


async def main():
    # -u for unbuffered stdout (some issues with async code/autoflushing)
    global events_to_process_mt_queue, events_to_process_async_queue

    events_to_process_mt_queue = queue.Queue()  # thread safe queue, no async support.
    events_to_process_async_queue = asyncio.Queue()  # async Queue, not thread safe

    if False:
        # Unreliable -- some files missing.
        observer = Observer()
        event_handler = HasteFSEventHandler(put_event_on_queue)
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
    else:
        # poll instead. this approach doesnt support subfolders
        poll_thread = threading.Thread(target=thread_worker_poll_fs, daemon=True)
        poll_thread.start()

    # Create workers to process events from the queue.
    # Here, there is a single worker thread.
    tasks = []

    task = asyncio.create_task(xfer_events_from_fs(f'events-xfer'))
    tasks.append(task)

    for i in range(x_preprocessing_cores):
        task = asyncio.create_task(preprocess_async_loop(f'preprocess-{i}', events_to_process_async_queue))
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

    if observer is not None:
        observer.join()


if __name__ == '__main__':
    if True:
        asyncio.run(main())
    else:
        # Debug mode.
        EventLoopDelayMonitor(interval=1)

        # (couldn't find anything)
        # https://stackoverflow.com/questions/38856410/monitoring-the-asyncio-event-loop
        loop = asyncio.get_event_loop()
        loop.slow_callback_duration = TOO_LONG
        loop.set_debug(True)  # Enable debug
        loop.run_until_complete(main())
