import logging
import time

import numpy as np
from haste_storage_client.models.interestingness_model import InterestingnessModel
from scipy.interpolate import interp1d


class EstimatedPreprocessingEfficacyInterestingnessModel(InterestingnessModel):
    """
    An interestingness model which computes an interestingness for all items on the queue based on the efficacy (i.e. file size reduction for CPU time) of a pre-processing function.
    """

    def __init__(self):
        pass

    def interestingness(self, stream_id=None, timestamp=None, location=None, substream_id=None, metadata=None, mongo_collection=None):
        """
        :param stream_id (str): ID for the stream session - used to group all the data for that streaming session.
        :param timestamp (numeric): should come from the cloud edge (eg. microscope). integer or floating point.
            *Uniquely identifies the document within the streaming session*.
        :param location (tuple): spatial information (eg. (x,y)).
        :param substream_id (string): ID for grouping of documents in stream (eg. microscopy well ID), or 'None'.
        :param metadata (dict): extracted metadata (eg. image features).
        :param mongo_collection: context-specific collection for the context (e.g. mongoDB) allowing interestingness functions to use information related to other documents in the stream. Named for backwards compatibility.
        """

        # The interestingness models used for the Tiered Storage systems use an interestingness function which is a function of a single document.
        # In this case, the interestingness of all documents depends on all other documents.
        # We use the same API for both cases, for now.

        # context_collection is in this case, the parent queue.

        start = time.time()

        # Fit the spline:
        to_fit_indices = (mongo_collection.known_scores > 0)

        if np.sum(to_fit_indices) > 3:
            to_fit_X = mongo_collection.index[to_fit_indices]
            to_fit_Y = mongo_collection.known_scores[to_fit_indices]

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

            mongo_collection.estimated_scores[min_interpolate_range:max_interpolate_range + 1] = f(
                mongo_collection.index[min_interpolate_range:max_interpolate_range + 1])

            mongo_collection.estimated_scores[0:min_interpolate_range] = mongo_collection.estimated_scores[min_interpolate_range]
            mongo_collection.estimated_scores[max_interpolate_range + 1:-1] = mongo_collection.estimated_scores[max_interpolate_range]

            # min_estimated_score = np.min(context_collection.estimated_scores)
            #
            # if min_estimated_score <= 0:
            #     context_collection.estimated_scores = context_collection.estimated_scores + 1 + (-min_estimated_score)
            #
            # assert (np.min(context_collection.estimated_scores) >= 0)

            logging.info(
                f'{time.time()}* known_scores_are: *{mongo_collection.known_scores.tolist()}* states_are: *{mongo_collection.states.tolist()}*')

            logging.info(f'_update_estimated_scores took {time.time() - start}')

            if mongo_collection.mode == MODE_GOLDEN:
                mongo_collection.estimated_scores = mongo_collection.golden_estimated_interestingness_scores.copy()
