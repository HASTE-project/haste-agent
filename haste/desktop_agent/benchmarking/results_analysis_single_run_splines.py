import os


from haste.desktop_agent import golden
import matplotlib.pyplot as plt

# grep Queue_is_empty *.log
from haste.desktop_agent.config import QUIT_AFTER
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

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

from haste.desktop_agent.benchmarking.benchmarking_analysis_config import get_run_streamid_tag_filename_grepped
RUN, stream_id, tag, filename, filename_grepped = get_run_streamid_tag_filename_grepped()


print(os.getcwd())

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
            elif action == 'POP_PREPROCESS':
                x_preprocess_times.append(time)
                y_preprocess_indices.append(index)
            elif action == 'POP_PREPROCESS_SEARCH':
                x_preprocess_search_times.append(time)
                y_preprocess_search_indices.append(index)
            elif action == 'POP_SEND':
                x_send_times.append(time)
                y_send_indices.append(index)
            elif action == 'POP_SEND_PRE':
                # plot them in the same color
                x_send_times.append(time)
                y_send_indices.append(index)
            else:
                raise (Exception())

top_index = QUIT_AFTER
golden_compressibility = (golden.csv_results['input_file_size_bytes'] - golden.csv_results['output_file_size_bytes']) / \
                         golden.csv_results['duration_total']
#golden_compressibility = golden_compressibility[:QUIT_AFTER]
golden_compressibility = np.array(golden_compressibility)
golden_compressibility_tiled = np.tile(golden_compressibility, (4, 1))
golden_compressibility_tiled = np.transpose(golden_compressibility_tiled)

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

# don't draw the splines one.
#sys.exit()

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
