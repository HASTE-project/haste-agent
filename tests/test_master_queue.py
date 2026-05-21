from haste.desktop_agent.config import MODE_NATURAL, MODE_GOLDEN
from haste.desktop_agent.master_queue import MasterQueue, STATE_NO_FILE, STATE_UNSENT_NOT_PRE_PROCESSED, \
    STATE_PRE_PROCESSING, STATE_SENDING, STATE_SENT, STATE_UNSENT_PRE_PROCESSED
import numpy as np


def test_master_queue_golden():
    q = MasterQueue(5, MODE_GOLDEN, np.array([1, 2, 3, 4, 5], dtype=np.float))
    assert ((q.states == STATE_NO_FILE).all())

    for i in range(5):
        q.new_file({})

    assert ((q.states == STATE_UNSENT_NOT_PRE_PROCESSED).all())

    ###

    index, _ = q.pop_file_to_preprocess()
    assert (index == 4)
    assert (q.states[4] == STATE_PRE_PROCESSING)

    index, _ = q.pop_file_to_send()
    assert (index == 0)
    assert (q.states[0] == STATE_SENDING)

    q.notify_file_preprocessed(4,1,{})
    q.notify_file_sent(0)

    assert np.all(q.states == np.array([
        STATE_SENT,
        STATE_UNSENT_NOT_PRE_PROCESSED,
        STATE_UNSENT_NOT_PRE_PROCESSED,
        STATE_UNSENT_NOT_PRE_PROCESSED,
        STATE_UNSENT_PRE_PROCESSED
    ]))

    ###

    index, _ = q.pop_file_to_preprocess()
    assert (index == 3)
    assert (q.states[3] == STATE_PRE_PROCESSING)

    index, _ = q.pop_file_to_send()
    assert (index == 4)
    assert (q.states[4] == STATE_SENDING)

    q.notify_file_preprocessed(3,1,{})
    q.notify_file_sent(4)

    assert np.all(q.states == np.array([
        STATE_SENT,
        STATE_UNSENT_NOT_PRE_PROCESSED,
        STATE_UNSENT_NOT_PRE_PROCESSED,
        STATE_UNSENT_PRE_PROCESSED,
        STATE_SENT
    ]))
