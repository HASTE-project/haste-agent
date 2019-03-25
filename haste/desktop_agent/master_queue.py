import logging

from haste.desktop_agent.config import LOGGING_FORMAT_AGENT, LOGGING_FORMAT_DATE
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

STATE_NO_FILE = 0
STATE_UNSENT_NOT_PRE_PROCESSED = 1
STATE_PRECPROCESSING = 2
STATE_UNSENT_PRE_PROCESSED = 3
STATE_SENDING = 4
STATE_SENT = 5


class MasterQueue:
    debug_fig_index = 0
    foo = 0

    def __init__(self, capacity):

        logging.basicConfig(level=logging.INFO,
                            format=LOGGING_FORMAT_AGENT,
                            datefmt=LOGGING_FORMAT_DATE)

        logging.info(f'current directory is: {os.getcwd()}')
        logging.debug(f'command line args arg: {sys.argv}')

        self.filepaths = []
        assert STATE_NO_FILE == 0
        self.states = np.zeros(capacity, dtype=np.int)
        self.known_scores = np.full(capacity, -1)
        self.estimated_scores = np.ones(capacity)
        self.index = np.arange(0, capacity)

    def new_file(self, filepath):
        self.filepaths.append(filepath)
        index = len(self.filepaths) - 1
        self.states[index] = STATE_UNSENT_NOT_PRE_PROCESSED

        logging.info(f'PLOT - NEW_FILE - {index}')

    def pop_file_to_send(self):
        indices_where_unsent_preprocessed = np.where(self.states == STATE_UNSENT_PRE_PROCESSED)[0]

        if len(indices_where_unsent_preprocessed) > 0:
            # Send one of the preprocessed files:
            index_to_send = np.random.choice(indices_where_unsent_preprocessed)
            self.states[index_to_send] = STATE_SENDING
            return index_to_send, self.filepaths[index_to_send]
        else:
            # TODO: messy...
            assert np.min(self.estimated_scores) >= 0
            max_est_score = np.max(self.estimated_scores)

            inverted_estimated_scores_unprocessed_and_zeros = (self.states == STATE_UNSENT_NOT_PRE_PROCESSED) * (
                    (max_est_score + 1) - self.estimated_scores)
            lowest_score = np.max(inverted_estimated_scores_unprocessed_and_zeros)

            if lowest_score == 0:
                # There is no 'STATE_UNSENT_NOT_PPROCED' file.
                return None, None
            else:
                indices_of_min_score = np.where(inverted_estimated_scores_unprocessed_and_zeros == lowest_score)[0]
                index_to_send = np.random.choice(indices_of_min_score)
                self.states[index_to_send] = STATE_SENDING

                logging.info(f'PLOT - POP_SEND - {index_to_send}')

                return index_to_send, self.filepaths[index_to_send]

    def pop_file_to_preprocess(self):
        estimated_scores_unprocessed = (self.states == STATE_UNSENT_NOT_PRE_PROCESSED) * (self.estimated_scores)
        max_score = np.max(estimated_scores_unprocessed)
        indexes_at_max = np.where(estimated_scores_unprocessed == max_score)[0]
        index_to_process = np.random.choice(indexes_at_max)

        if self.states[index_to_process] == STATE_UNSENT_NOT_PRE_PROCESSED:
            self.states[index_to_process] = STATE_PRECPROCESSING

            logging.info(f'PLOT - POP_PREPROCESS - {index_to_process}')

            return index_to_process, self.filepaths[index_to_process]
        else:
            return None, None

    def notify_file_sent(self, index):
        current_state = self.states[index]
        assert current_state == STATE_SENDING
        self.states[index] = STATE_SENT

    def notify_file_preprocessed(self, index, score, new_filepath):
        current_state = self.states[index]
        assert current_state == STATE_PRECPROCESSING
        self.states[index] = STATE_UNSENT_PRE_PROCESSED
        self.known_scores[index] = score
        self.filepaths[index] = new_filepath

        self._update_estimated_scores()

    def _update_estimated_scores(self):
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

            plt.plot(self.index, self.estimated_scores)
            plt.savefig(f'figures/0.splines.{self.debug_fig_index}.png')
            self.debug_fig_index += 1

            min_estimated_score = np.min(self.estimated_scores)

            if min_estimated_score < 0:
                self.estimated_scores = self.estimated_scores + 1 + (-min_estimated_score)

            assert (np.min(self.estimated_scores) >= 0)


import random

if __name__ == '__main__':
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
