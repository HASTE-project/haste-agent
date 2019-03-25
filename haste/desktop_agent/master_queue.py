from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np

STATE_NO_FILE = 0
STATE_UNSENT_NOT_PPROCED = 1
STATE_PRECPROCESSING = 2
STATE_UNSENT_PPROCED = 3
STATE_SENDING = 4
STATE_SENT = 5


class MasterQueue:
    debug_fig_index = 0
    foo = 0

    def __init__(self, capacity):
        self.filepaths = []
        self.states = np.zeros(capacity, dtype=np.int)
        self.known_scores = np.full(capacity, -1)
        self.estimated_scores = np.ones(capacity)
        self.index = np.arange(0, capacity)

    def new_file(self, filepath):
        self.filepaths.append(filepath)
        index = len(self.filepaths) - 1
        self.states[index] = STATE_UNSENT_NOT_PPROCED

    def pop_file_to_send(self):
        # First, check for any preprocessed (and unsent files)

        estimated_scores_processed = (self.states == STATE_UNSENT_PPROCED)
        index_of_true = np.argmax(estimated_scores_processed)
        # verify it is actually preprocessed
        if estimated_scores_processed[index_of_true] == True:
            # send this file:
            self.states[index_of_true] = STATE_SENDING
            return index_of_true, self.filepaths[index_of_true]
        else:
            estimated_scores_unprocessed = (self.states == STATE_UNSENT_NOT_PPROCED) * -(self.estimated_scores)
            index_to_process = np.argmin(estimated_scores_unprocessed)
            if self.states[index_to_process] == STATE_UNSENT_NOT_PPROCED:
                self.states[index_to_process] = STATE_SENDING
                return index_to_process, self.filepaths[index_to_process]
            else:
                return None, None

    def pop_file_to_preproc(self):
        estimated_scores_unprocessed = (self.states == STATE_UNSENT_NOT_PPROCED) * (self.estimated_scores)
        max_score = np.max(estimated_scores_unprocessed)
        indexes_at_max = np.where(estimated_scores_unprocessed == max_score)[0]
        index_to_process = np.random.choice(indexes_at_max)

        if self.states[index_to_process] == STATE_UNSENT_NOT_PPROCED:
            self.states[index_to_process] = STATE_PRECPROCESSING
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
        self.states[index] = STATE_UNSENT_PPROCED
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

            if False:
                # Linear spline
                f = interp1d(to_fit_X, to_fit_Y, assume_sorted=True)
            else:
                # Cubic spline
                f = interp1d(to_fit_X, to_fit_Y, assume_sorted=True, kind='cubic')

            self.estimated_scores[min_interpolate_range:max_interpolate_range + 1] = f(
                self.index[min_interpolate_range:max_interpolate_range + 1])

            self.estimated_scores[0:min_interpolate_range] = self.estimated_scores[min_interpolate_range]
            self.estimated_scores[max_interpolate_range+1:-1] = self.estimated_scores[max_interpolate_range]

            plt.plot(self.index, self.estimated_scores)
            plt.savefig(f'figures/0.splines.{self.debug_fig_index}.png')
            self.debug_fig_index += 1

            min_estimated_score = np.min(self.estimated_scores)

            if min_estimated_score < 0:
                self.estimated_scores = self.estimated_scores + 1 + (-min_estimated_score)

            assert(np.min(self.estimated_scores) >= 0)





import random

if __name__ == '__main__':
    mq = MasterQueue(20)
    for i in range(0, 20):
        mq.new_file(f'file_{i}')

    for i in range(20):
        index, filepath = mq.pop_file_to_preproc()
        assert index is not None
        mq.notify_file_preprocessed(index, random.randint(1, 101), f'new_file_{i}')

    for i in range(10):
        mq.pop_file_to_send()
