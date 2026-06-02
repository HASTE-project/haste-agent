import os

from haste.desktop_agent import golden
import matplotlib.pyplot as plt

from haste.desktop_agent.benchmarking.benchmarking_analysis_config import get_run_streamid_tag_filename_grepped
RUN, stream_id, tag, filename, filename_grepped = get_run_streamid_tag_filename_grepped()

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


print(os.getcwd())

events = np.zeros((QUIT_AFTER, 5))

first_time = -1

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
            if first_time == -1:
                first_time = time
            time = time - first_time

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
                #x_send_times.append(time)
                #y_send_indices.append(index)
                events[index, COL_INDEX_POP_SEND] = time

                queue_length_x_times.append(time)
                queue_length_y_length.append(last_queue_length_y_length() - 1)
            else:
                raise Exception()

top_index = QUIT_AFTER

# The offline NMSR values, used in some plots.
golden_compressibility = (golden.csv_results['input_file_size_bytes'] - golden.csv_results['output_file_size_bytes']) / \
                         golden.csv_results['duration_total']
#golden_compressibility = golden_compressibility[:QUIT_AFTER]
golden_compressibility = np.array(golden_compressibility)
golden_compressibility_tiled = np.tile(golden_compressibility, (4, 1))
golden_compressibility_tiled = np.transpose(golden_compressibility_tiled)


# --------------------------------------------------------------------------------------------------------
if False:
    # The one with the green/blue background, not used in paper

    fig, ax2 = plt.subplots()

    ax2.imshow(golden_compressibility_tiled, interpolation='nearest', aspect='auto', zorder=3)
    ax2.legend()

    ax = ax2.twiny()
    ax.plot(x_new_file_times, y_new_file_indices, color='r', zorder=2, label='new_files')
    ax.scatter(x_send_times, y_send_indices, color='m', zorder=2, label='send')
    ax.scatter(x_preprocess_times, y_preprocess_indices, color='w', zorder=2, label='prepcess')
    ax.scatter(x_preprocess_search_times, y_preprocess_search_indices, color='y', zorder=2, label='prepcess_search')
    ax.legend()

    plt.show()
    fig.savefig(f'figures/{stream_id}.0.overall.png')
    fig.clf()

# --------------------------------------------------------------------------------------------------------

capacity = QUIT_AFTER
index = np.arange(0, capacity)

def fit_spline(known_scores):
    # Fit the spline:
    to_fit_indices = (known_scores > 0)

    if np.sum(to_fit_indices) > 3:
        to_fit_X = index[to_fit_indices]
        to_fit_Y = known_scores[to_fit_indices]

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

        # estimated_scores[min_interpolate_range:max_interpolate_range + 1] = f(
        #     index[min_interpolate_range:max_interpolate_range + 1])
        #
        # estimated_scores[0:min_interpolate_range] = estimated_scores[min_interpolate_range]
        # estimated_scores[max_interpolate_range + 1:-1] = estimated_scores[max_interpolate_range]

        # binding?
        return f, min_interpolate_range, max_interpolate_range
    else:
        return None, None, None


plt.clf()

##########################################################################################
# plots not used in the paper.

plt.figure(figsize=(7, 3.5), dpi=500)

if False: # print the golden NMSR as a line
    X2 = np.arange(0, capacity, 1)
    Y2 = golden_compressibility
    plt.plot(X2, Y2, color=(1, 0, 0, 0.5))

if False: # Print the intermediate revision of the splines
    if True:
        for i, scores in enumerate(spline_scores[::5]):
            f, min, max = fit_spline(scores)
            if f is not None:
                num_steps = int((max - min) / capacity * 1000)
                X = np.linspace(min, max, num_steps, endpoint=True)
                plt.plot(X, f(X), color=(0, 0.1, 1, 0.2 + (i / capacity)**5 * 0.3))

    # The final revision of the splines
    if True:
        scores = spline_scores[-1]
        f, min, max = fit_spline(scores)
        if f is not None:
            num_steps = int((max - min) / capacity * 1000)
            X = np.linspace(min, max, num_steps, endpoint=True)
            plt.plot(X, f(X), color=(0, 1, 0))



if False: # different colours for pre-processed and not.
    X_files_that_were_preprocessed = []
    Y_files_that_were_preprocessed = []

    for spline_state in spline_states:
        for i in range(len(spline_state)):
            state = spline_state[i]
            if state == 2 or state == 3:
                if i not in X_files_that_were_preprocessed:
                    X_files_that_were_preprocessed.append(i)
                    Y_files_that_were_preprocessed.append(golden_compressibility[i])

    #
    if True:
        plt.scatter(X_files_that_were_preprocessed, Y_files_that_were_preprocessed)

    X_files_that_were_not_preprocessed = []
    Y_files_that_were_not_preprocessed = []

    for i in range(len(spline_states[0])):
        if i not in X_files_that_were_preprocessed:
            X_files_that_were_not_preprocessed.append(i)
            Y_files_that_were_not_preprocessed.append(golden_compressibility[i])

    #
    if True:
        plt.scatter(X_files_that_were_not_preprocessed, Y_files_that_were_not_preprocessed)


    plt.savefig(f'figures/{stream_id}.1.splines-blended-ver2.png')


##########################################################################################


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

    plt.savefig(f'figures/{stream_id}.0.overall.ver3.png')


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

    plt.savefig(f'figures/{stream_id}.0.overall-sorted-golden.ver3.png')




#for row in events[events[:,COL_INDEX_POP_PREPROC] > 0]:
#    plt.plot(row[COL_INDEX_TIME_NEW_FILE], row[COL_INDEX_FILE_INDEX], row[COL_INDEX_TIME_POP_PROEPROC_SEARCH], row[COL_INDEX_FILE_INDEX], 'o')

#ax.plot(x_new_file_times, y_new_file_indices, color='r', zorder=2, label='new_files')
#ax.scatter(x_send_times, y_send_indices, color='m', zorder=2, label='send')
#ax.scatter(x_preprocess_times, y_preprocess_indices, color='b', zorder=2, label='prepcess')
#ax.scatter(x_preprocess_search_times, y_preprocess_search_indices, color='y', zorder=2, label='prepcess_search')

#ax.legend()

#plt.show()

import create_3d_plot



if True: # print the golden NMSR as a scatter
    plt.clf()
    capacity = QUIT_AFTER
    X2 = np.arange(0, capacity, 1)
    Y2 = golden_compressibility

    start = 200
    end = 301
    X2 = X2[start:end]
    Y2 = Y2[start:end]
    plt.plot(X2, Y2, marker='o')

    plt.xlabel(create_3d_plot.AXIS_LABEL_MESSAGE_INDEX)
    plt.ylabel(create_3d_plot.AXIS_LABEL_TRUE_NMSR)

    plt.savefig(f'figures/{stream_id}.1.golden-simple.png')
    plt.clf()



# 'Descent A' >> saved manually as 11_fri_am.3d.descentA.png
#start_index = 350
#end_index = 450
#legend = ['Ordering (Message Arrival Index)', 'Ordering (Processing Time)']
#create_3d_plot.plot(golden_compressibility, y_preprocess_indices, x_preprocess_times, 350, 450, legend )


#start_index, end_index = 550, 600
start_index, end_index = 575, 688
legend = ['Ordering (Message Arrival Index)', 'Ordering (Upload Time)']
create_3d_plot.plot(golden_compressibility, y_send_indices, y_send_indices, start_index, end_index, legend)

# --------------------------------------------------------------------------------------------------------
