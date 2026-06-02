import os
import sys

from haste.desktop_agent import golden
from haste.desktop_agent.benchmarking.__main__ import CONFIGS


# grep Queue_is_empty *.log
from haste.desktop_agent.config import QUIT_AFTER

import numpy as np
from scipy.interpolate import interp1d


COL_INDEX_FILE_INDEX = 0
COL_INDEX_TIME_NEW_FILE = 1
COL_INDEX_POP_SEND = 2
COL_INDEX_TIME_POP_PREPROC_SEARCH = 3
COL_INDEX_TIME_POP_PREPROC = 4

x_new_file_times = []
y_new_file_indices = []
x_preprocess_times = []
y_preprocess_indices = []
x_preprocess_search_times = []
y_preprocess_search_indices = []
x_send_times = []
y_send_indices = []

spline_scores = []
spline_states = []

queue_length_x_times = []
queue_length_y_length = []

def last_queue_length_y_length():
    return queue_length_y_length[-1] if len(queue_length_y_length) > 0 else 0

# 2019-03-25 15:59:01.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525941.7687411 - NEW_FILE - 49
# 2019-03-25 15:59:02.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525942.1522071 - POP_PREPROCESS - 17
# 2019-03-25 15:59:02.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525942.2393758 - POP_PREPROCESS - 18
# 2019-03-25 15:59:02.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525942.253982 - POP_SEND - 49


#input()

# run = '2019_04_29-03'
#stream_id = 'agent_log_2019_04_29__10_29_35_trash'#

run = '11_fri_am'
#stream_id = 'agent_log_2019_03_29__11_18_21_trash'
stream_id = 'agent_log_2019_03_29__11_18_21_trash'
#stream_id = 'agent_log_2019_03_29__11_30_37_trash'

stream_id = stream_id.replace('agent_log_', '')
stream_id = stream_id.replace('.log', '')

if run is not None:
    filename = f'logs/{run}/agent_log_{stream_id}.log'
else:
    filename = f'../../../logs/agent_log_{stream_id}.log'

if not filename.endswith('.log'):
    filename += '.log'

print(os.getcwd())

events = np.zeros((QUIT_AFTER, 5))


# with open(f'logs/2_tues_am_office/agent_log_2019_03_26__10_10_21_trash.log') as f:
with open(filename) as f:
    for line in f.readlines():

        if line == '\n':
            continue

        if 'known_scores_are' in line:
            print(line)
            s = line.split('*')
            known_scores = np.array(eval(s[-4]))
            states_are = np.array(eval(s[-2]))
            spline_scores.append(known_scores)
            spline_states.append(states_are)

        elif 'PLOT_QUEUE' in line:
            s = line.split(' ')
            time = float(s[-5])
            action = s[-3]
            index = int(s[-1])

            if action == 'NEW_FILE':
                x_new_file_times.append(time)
                y_new_file_indices.append(index)
                events[index, COL_INDEX_FILE_INDEX] = index
                events[index, COL_INDEX_TIME_NEW_FILE] = time

                queue_length_x_times.append(time)
                queue_length_y_length.append(last_queue_length_y_length() + 1)

            elif action == 'POP_PREPROCESS':
                x_preprocess_times.append(time)
                y_preprocess_indices.append(index)
                events[index, COL_INDEX_TIME_POP_PREPROC] = time

                #queue_length_x_times.append(time)
                #queue_length_y_length.append(last_queue_length_y_length() - 1)

            elif action == 'POP_PREPROCESS_SEARCH':
                x_preprocess_search_times.append(time)
                y_preprocess_search_indices.append(index)
                events[index, COL_INDEX_TIME_POP_PREPROC_SEARCH] = time

                #queue_length_x_times.append(time)
                #queue_length_y_length.append(last_queue_length_y_length() - 1)

            elif action == 'POP_SEND':
                x_send_times.append(time)
                y_send_indices.append(index)
                events[index, COL_INDEX_POP_SEND] = time

                queue_length_x_times.append(time)
                queue_length_y_length.append(last_queue_length_y_length() - 1)

            elif action == 'POP_SEND_PRE':
                # plot them in the same color
                x_send_times.append(time)
                y_send_indices.append(index)
                events[index, COL_INDEX_POP_SEND] = time

                queue_length_x_times.append(time)
                queue_length_y_length.append(last_queue_length_y_length() - 1)
            else:
                raise Exception()

top_index = QUIT_AFTER
golden_compressibility = (golden.csv_results['input_file_size_bytes'] - golden.csv_results['output_file_size_bytes']) / \
                         golden.csv_results['duration_total']
#golden_compressibility = golden_compressibility[:QUIT_AFTER]
golden_compressibility = np.array(golden_compressibility)
golden_compressibility_tiled = np.tile(golden_compressibility, (4, 1))
golden_compressibility_tiled = np.transpose(golden_compressibility_tiled)

#fig, ax2 = plt.subplots()

#ax2.imshow(golden_compressibility_tiled, interpolation='nearest', aspect='auto', zorder=3)
#ax2.legend()




import matplotlib.pyplot as plt

fig, (ax_golden, ax_element_lifetime_plot) = plt.subplots(
    1, 2,
    #sharey=True,
    figsize=(8, 6),
    #gridspec_kw={"height_ratios": [1, 3]}  # top smaller, bottom larger
)

# x1, y1 = np.array([-1, 12]),np.array( [1, 4])
# x2, y2 = np.array([1, 10]), np.array([3, 2])
# plt.plot(x1, y1, x2, y2, marker = 'o')
#plt.plot((1,3), (2, 4), linestyle='--')
#plt.show()

print()

#ax = ax2.twiny()

#plt.xlim(0, 10)

#plt.plot(0,0, 10, 100, marker='o')

# plt.plot(np.transpose(events_with_pre_proc[:,COL_INDEX_TIME_NEW_FILE]),
#          np.transpose(events_with_pre_proc[:,COL_INDEX_FILE_INDEX]),
#                       np.transpose(events_with_pre_proc[:, COL_INDEX_TIME_POP_PREPROC]),
#                                    np.transpose(events_with_pre_proc[:,COL_INDEX_FILE_INDEX]),
#          marker='o')

# x axis as time, y axis as upload index.
if True:
    # Those pre-processed locally
    for row in events[events[:, COL_INDEX_TIME_POP_PREPROC] > 0]:
        print(row)
        ax_element_lifetime_plot.plot((row[COL_INDEX_TIME_NEW_FILE], row[COL_INDEX_TIME_POP_PREPROC]),
                                      (row[COL_INDEX_FILE_INDEX], row[COL_INDEX_FILE_INDEX]),
                 '-b')

    if False:
        # Those processed locally for the search
        for row in events[events[:, COL_INDEX_TIME_POP_PREPROC_SEARCH] > 0]:
            print(row)
            ax_element_lifetime_plot.plot((row[COL_INDEX_TIME_NEW_FILE], row[COL_INDEX_TIME_POP_PREPROC_SEARCH]),
                                          (row[COL_INDEX_FILE_INDEX], row[COL_INDEX_FILE_INDEX]),
                     '-r')

    # The ones uploaded without preprocessing
    for row in events[events[:, COL_INDEX_TIME_POP_PREPROC_SEARCH] + events[:, COL_INDEX_TIME_POP_PREPROC] == 0]:
        print(row)
        ax_element_lifetime_plot.plot(
            (row[COL_INDEX_TIME_NEW_FILE],row[COL_INDEX_POP_SEND]),
            (row[COL_INDEX_FILE_INDEX], row[COL_INDEX_FILE_INDEX]),
            '-g')

    if False:
        # This was queue length but its boring, just two straight lines...
        ax_top.plot(queue_length_x_times, queue_length_y_length, '-k')

    if True:
        ax_golden.plot(golden_compressibility, list(range(len(golden_compressibility))), "-b")

    plt.savefig(f'figures/{stream_id}.0.overall.ver2.png')




if True:
    # Those pre-processed locally
    for row in events[events[:, COL_INDEX_TIME_POP_PREPROC] > 0]:
        ax_element_lifetime_plot.plot(
            # (X1, X2) -> (Y1, Y2)
            (row[COL_INDEX_TIME_NEW_FILE], row[COL_INDEX_TIME_POP_PREPROC]),
                 #(row[COL_INDEX_FILE_INDEX], row[COL_INDEX_FILE_INDEX]),
                 (golden_compressibility[int(row[COL_INDEX_FILE_INDEX])],
                  golden_compressibility[int(row[COL_INDEX_FILE_INDEX])]),
                 '-b')


    # The ones uploaded without preprocessing
    for row in events[events[:, COL_INDEX_TIME_POP_PREPROC_SEARCH] + events[:, COL_INDEX_TIME_POP_PREPROC] == 0]:
        ax_element_lifetime_plot.plot(
            (row[COL_INDEX_TIME_NEW_FILE],row[COL_INDEX_POP_SEND]),
            (golden_compressibility[int(row[COL_INDEX_FILE_INDEX])],
             golden_compressibility[int(row[COL_INDEX_FILE_INDEX])]),
            '-g')

    plt.savefig(f'figures/{stream_id}.0.overall-sorted-golden.ver2.png')




#for row in events[events[:,COL_INDEX_POP_PREPROC] > 0]:
#    plt.plot(row[COL_INDEX_TIME_NEW_FILE], row[COL_INDEX_FILE_INDEX], row[COL_INDEX_TIME_POP_PROEPROC_SEARCH], row[COL_INDEX_FILE_INDEX], 'o')

#ax.plot(x_new_file_times, y_new_file_indices, color='r', zorder=2, label='new_files')
#ax.scatter(x_send_times, y_send_indices, color='m', zorder=2, label='send')
#ax.scatter(x_preprocess_times, y_preprocess_indices, color='b', zorder=2, label='prepcess')
#ax.scatter(x_preprocess_search_times, y_preprocess_search_indices, color='y', zorder=2, label='prepcess_search')

#ax.legend()

#plt.show()




# --------------------------------------------------------------------------------------------------------
