from haste.desktop_agent import golden
from haste.desktop_agent.benchmarking.__main__ import CONFIGS
import matplotlib.pyplot as plt

# grep Queue_is_empty *.log
from haste.desktop_agent.config import QUIT_AFTER

x_new_file_times = []
y_new_file_indices = []

x_preprocess_times = []
y_preprocess_indices = []

x_preprocess_search_times = []
y_preprocess_search_indices = []

x_send_times = []
y_send_indices = []

# 2019-03-25 15:59:01.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525941.7687411 - NEW_FILE - 49
# 2019-03-25 15:59:02.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525942.1522071 - POP_PREPROCESS - 17
# 2019-03-25 15:59:02.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525942.2393758 - POP_PREPROCESS - 18
# 2019-03-25 15:59:02.253 - AGENT - MainThread - INFO - PLOT_QUEUE - 1553525942.253982 - POP_SEND - 49

stream_id = '2019_03_25__17_34_20_trash'

with open(f'../../../logs/agent_log_{stream_id}.log') as f:
    for line in f.readlines():
        if 'PLOT_QUEUE' in line:
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

import matplotlib.pyplot as plt

top_index = QUIT_AFTER

foo = (golden.csv_results['input_file_size_bytes'] - golden.csv_results['output_file_size_bytes']) / golden.csv_results[
    'duration_total']

foo = foo[:QUIT_AFTER]

import numpy as np

foo = np.array(foo)

bar = np.tile(foo, (4, 1))

bar = np.transpose(bar)

# plt.ylim(0, QUIT_AFTER)
# plt.xlim(min(x_new_file_times), max(x_send_times))


# ax.axis('off')

fig, ax2 = plt.subplots()

ax2.imshow(bar, interpolation='nearest', aspect='auto', zorder=3)
ax2.legend()

ax = ax2.twiny()
ax.plot(x_new_file_times, y_new_file_indices, color='r', zorder=2, label='new_files')
ax.scatter(x_send_times, y_send_indices, color='m', zorder=2, label='send')
ax.scatter(x_preprocess_times, y_preprocess_indices, color='w', zorder=2, label='prepcess')
ax.scatter(x_preprocess_search_times, y_preprocess_search_indices, color='y', zorder=2, label='prepcess_search')
ax.legend()

plt.show()
fig.savefig(f'figures/0.overall.{stream_id}.png')
