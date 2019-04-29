import logging

from haste.desktop_agent.config import LOGGING_FORMAT_AGENT, LOGGING_FORMAT_DATE, MODE_SPLINES, MODE_GOLDEN, \
    MODE_NATURAL
from scipy.interpolate import interp1d
import numpy as np
import time

STATE_NO_FILE = 0
STATE_UNSENT_NOT_PRE_PROCESSED = 1
STATE_PRE_PROCESSING = 2
STATE_UNSENT_PRE_PROCESSED = 3
STATE_SENDING = 4
STATE_SENT = 5

BLOCK_SIZE = 15


class MasterQueue:
    debug_fig_index = 0

    count_files_preprocessed = 0

    def __init__(self, capacity, mode, golden_estimated_scores):
        logging.basicConfig(level=logging.INFO,
                            format=LOGGING_FORMAT_AGENT,
                            datefmt=LOGGING_FORMAT_DATE)
        self.infos = []
        self.states = np.full(capacity, STATE_NO_FILE)
        self.index = np.arange(0, capacity)
        self.index.flags['WRITEABLE'] = False
        self.mode = mode
        self.golden_estimated_scores = golden_estimated_scores
        self.golden_estimated_scores.flags['WRITEABLE'] = False

        logging.info(f'Mode is {["SPLINES", "NATURAL", "GOLDEN"][mode]}')

        self.known_scores = np.full(capacity, -1)

        # Use the ground truth as a baseline.

        if self.mode == MODE_GOLDEN:
            self.estimated_scores = self.golden_estimated_scores.copy()
        else:
            self.estimated_scores = np.ones(capacity, dtype=np.float)

    def new_file(self, info):
        self.infos.append(info)
        index = len(self.infos) - 1
        self.states[index] = STATE_UNSENT_NOT_PRE_PROCESSED
        logging.info(f'PLOT_QUEUE - {time.time()} - NEW_FILE - {index}')

    def pop_file_to_send(self):
        if np.sum(self.states == STATE_UNSENT_PRE_PROCESSED) > 0:
            logging.debug('Send the first preprocessed file:')
            index_to_send = np.argmax(self.states == STATE_UNSENT_PRE_PROCESSED)
        elif np.sum(self.states == STATE_UNSENT_NOT_PRE_PROCESSED) == 0:
            logging.info('no files to send at the moment')
            index_to_send = None
        elif self.mode == MODE_SPLINES or self.mode == MODE_GOLDEN:
            # We're trying to send the one with the lowest overall score, in the state STATE_UNSENT_NOT_PRE_PROCESSED
            est_scores = self.estimated_scores.copy()
            est_scores[self.states != STATE_UNSENT_NOT_PRE_PROCESSED] = np.nan
            index_to_send = np.nanargmin(est_scores)
        elif self.mode == MODE_NATURAL:
            # Note, False < True...  -- get the first true index
            # (we checked that we definitely had one to send at the top)
            index_to_send = np.argmax(self.states == STATE_UNSENT_NOT_PRE_PROCESSED)
        else:
            raise Exception(f'mode {self.mode} not known')

        if index_to_send is None:
            return None, None
        logging.info(f'PLOT_QUEUE - {time.time()} - POP_SEND_PRE - {index_to_send}')
        self.states[index_to_send] = STATE_SENDING
        return index_to_send, self.infos[index_to_send]

    def pop_file_to_preprocess(self):
        unprocessed_files = self.states == STATE_UNSENT_NOT_PRE_PROCESSED

        if np.sum(unprocessed_files) == 0:
            logging.info('No files to preprocess')
            index_to_process = None
        elif self.mode == MODE_SPLINES:
            index_to_process = None

            # first, search any blocks where we we haven't searched already:
            for block_start in range(0, len(self.infos), BLOCK_SIZE):
                block_end_excl = min(block_start + BLOCK_SIZE, len(self.infos))

                logging.info(f'block start,end_excl: {block_start, block_end_excl}')

                none_in_block_available_for_preprocessing = not np.any(
                    self.states[block_start:block_end_excl] == STATE_UNSENT_NOT_PRE_PROCESSED)
                some_in_block_already_known_score = np.any(self.known_scores[block_start:block_end_excl] >= 0) or np.any(
                    self.states[block_start:block_end_excl] == STATE_PRE_PROCESSING)

                if none_in_block_available_for_preprocessing or some_in_block_already_known_score:
                    continue
                else:
                    index_to_process = block_start + np.argmax(
                        self.states[block_start:block_end_excl] == STATE_UNSENT_NOT_PRE_PROCESSED)
                    logging.info(f'PLOT_QUEUE - {time.time()} - POP_PREPROCESS_SEARCH - {index_to_process}')
                    break

            if index_to_process is None:
                # 'climb'
                est_scores = self.estimated_scores.copy()
                est_scores[self.states != STATE_UNSENT_NOT_PRE_PROCESSED] = np.nan
                index_to_process = np.nanargmax(est_scores)
                logging.info(f'PLOT_QUEUE - {time.time()} - POP_PREPROCESS - {index_to_process}')


        elif self.mode == MODE_GOLDEN:
            # 'climb'
            est_scores = self.estimated_scores.copy()
            est_scores[self.states != STATE_UNSENT_NOT_PRE_PROCESSED] = np.nan
            index_to_process = np.nanargmax(est_scores)
            logging.info(f'PLOT_QUEUE - {time.time()} - POP_PREPROCESS - {index_to_process}')

        elif self.mode == MODE_NATURAL:
            # Send next unprocessed file
            index_to_process = np.argmax(unprocessed_files)
            logging.info(f'PLOT_QUEUE - {time.time()} - POP_PREPROCESS - {index_to_process}')
        else:
            raise Exception('mode not known')

        if index_to_process is None:
            return None, None

        self.count_files_preprocessed += 1
        self.states[index_to_process] = STATE_PRE_PROCESSING
        return index_to_process, self.infos[index_to_process]

    def notify_file_sent(self, index):
        assert self.states[index] == STATE_SENDING
        self.states[index] = STATE_SENT

    def notify_file_preprocessed(self, index, score, new_info):
        assert self.states[index] == STATE_PRE_PROCESSING
        self.states[index] = STATE_UNSENT_PRE_PROCESSED
        self.known_scores[index] = score
        self.infos[index] = new_info

        self._update_estimated_scores()

    def log_queue_info(self):
        # Log info about the present state of the queue
        count_preprocessed = np.sum(self.states == STATE_UNSENT_PRE_PROCESSED)
        count_not_preprocessed = np.sum(self.states == STATE_UNSENT_NOT_PRE_PROCESSED)
        logging.info(f'PLOT - {time.time()} - {count_preprocessed} - {count_not_preprocessed}')

    def _update_estimated_scores(self):
        start = time.time()

        # Fit the spline:
        to_fit_indices = (self.known_scores > 0)

        if np.sum(to_fit_indices) > 3:
            to_fit_X = self.index[to_fit_indices]
            to_fit_Y = self.known_scores[to_fit_indices]

            # index of first 'True'
            min_interpolate_range = np.argmax(to_fit_indices)
            # index of last 'True'
            max_interpolate_range = len(to_fit_indices) - np.argmax(to_fit_indices[::-1]) - 1

            if True:
                # Linear spline
                f = interp1d(to_fit_X, to_fit_Y, assume_sorted=True)
            else:
                # Cubic spline
                f = interp1d(to_fit_X, to_fit_Y, assume_sorted=True, kind='cubic')

            self.estimated_scores[min_interpolate_range:max_interpolate_range + 1] = f(
                self.index[min_interpolate_range:max_interpolate_range + 1])

            self.estimated_scores[0:min_interpolate_range] = self.estimated_scores[min_interpolate_range]
            self.estimated_scores[max_interpolate_range + 1:-1] = self.estimated_scores[max_interpolate_range]

            # min_estimated_score = np.min(self.estimated_scores)
            #
            # if min_estimated_score <= 0:
            #     self.estimated_scores = self.estimated_scores + 1 + (-min_estimated_score)
            #
            # assert (np.min(self.estimated_scores) >= 0)

            logging.info(
                f'{time.time()}* known_scores_are: *{self.known_scores.tolist()}* states_are: *{self.states.tolist()}*')

            logging.info(f'_update_estimated_scores took {time.time() - start}')

            if self.mode == MODE_GOLDEN:
                self.estimated_scores = self.golden_estimated_scores.copy()

    def plot(self):
        # plt.plot(self.index, map(lambda filename: get_golden_prio_for_filename(filename), )

        plt.plot(self.index, self.estimated_scores)
        plt.savefig(f'figures/0.splines.{self.debug_fig_index}.png')
        self.debug_fig_index += 1


if __name__ == '__main__':
    import random

    mq = MasterQueue(20)
    for i in range(0, 20):
        mq.new_file(f'file_{i}')

    for i in range(20):
        index, filepath = mq.pop_file_to_preprocess()
        assert index is not None
        score = 15 + 5 * np.cos(index / 10 * 2 * np.pi) + random.randint(-2, 2)

        mq.notify_file_preprocessed(index, score, f'new_file_{i}')

    for i in range(10):
        mq.pop_file_to_send()
