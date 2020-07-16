import pandas as pd

from haste.desktop_agent.benchmarking.__main__ import CONFIGS
import matplotlib.pyplot as plt

# from haste.desktop_agent.config import MODE_NATURAL, MODE_GOLDEN, MODE_SPLINES

# now in hsc
MODE_SPLINES = 0
MODE_NATURAL = 1
MODE_GOLDEN = 2


# RUN = '2019_05_08-01'
RUN = '11_fri_am'

# grep Queue_is_empty *.log > grepped.txt

# agent_log_2019_03_24__01_07_06_trash.log:2019-03-24 01:12:22.243 - AGENT - MainThread - INFO - Queue_is_empty. Duration since first event: 311.5138850212097 - total_bytes_sent: 315629743

with open(f'logs/{RUN}/grepped.txt') as f:
    lines = f.readlines()
    lines.sort()  # timestamp of each run at the start of the filename
    # assert len(lines) == 25

    count_preproc_threads = []
    mode = []
    source_dir = []
    time_taken = []
    bytes_sent = []

    for i, line in enumerate(lines):
        config = CONFIGS[i % len(CONFIGS)]
        print(config)
        print(line)
        print('---')

        count_preproc_threads.append(config[0])
        mode.append(config[2])
        source_dir.append(config[1].split('/')[-2])
        log_line = line.split(' ')

        # TODO: fix this
        time_taken.append(float(log_line[14]))
        bytes_sent.append(float(log_line[17]))


data = {
    'count_preproc_threads': count_preproc_threads,
    'mode': mode,
    'source_dir': source_dir,
    'time_taken': time_taken,
    'bytes_sent': bytes_sent
}
df = pd.DataFrame(data,
                  columns=['count_preproc_threads', 'mode', 'source_dir', 'time_taken', 'bytes_sent'])

plt.clf()
boxes = [
    df['time_taken'][
        (df['count_preproc_threads'] == 0) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    # df['time_taken'][
    #     (df['count_preproc_threads'] == 1) & (df['mode'] == MODE_GOLDEN) & (df['source_dir'] == 'greyscale')].values,
    df['time_taken'][
        (df['count_preproc_threads'] == 1) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')].values,
    df['time_taken'][
        (df['count_preproc_threads'] == 2) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')].values,
    df['time_taken'][
        (df['count_preproc_threads'] == 3) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')].values,

    df['time_taken'][
        (df['count_preproc_threads'] == 1) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    df['time_taken'][
        (df['count_preproc_threads'] == 2) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    # df['time_taken'][
    #     (df['count_preproc_threads'] == 2) & (df['mode'] == MODE_GOLDEN) & (df['source_dir'] == 'greyscale')].values,
    df['time_taken'][
        (df['count_preproc_threads'] == 3) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    # df['time_taken'][(df['count_preproc_threads'] == 3) & (df['mode'] == MODE_GOLDEN) & (df['source_dir'] == 'greyscale')],
    # df['time_taken'][(df['count_preproc_threads'] == 3) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')],
    # df['time_taken'][(df['count_preproc_threads'] == 3) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')],

    df['time_taken'][(df['count_preproc_threads'] == 0) & (df['source_dir'] == 'ffill')].values,
]

plt.boxplot(boxes,
            labels=[
        '0,n',

        # 'g,1,g',
        '1,s',
        '2,s',
        '3,s',

        '1,r',

        # 'g,2,g',
        '2,r',

        # 'g,3,g',
        # '3,s',
        '3,r',

        'ffill,0',
    ], whis='range')


# for cons with oliver
ax = plt.axes()
ax.yaxis.grid(alpha=0.3) # horizontal lines

plt.ylabel('End-to-end latency (seconds)')
plt.xlabel('Configuration')



plt.savefig(f'figures/{RUN}.0.boxwhisker.time_taken.png')

plt.clf()
plt.boxplot([
    df['bytes_sent'][
        (df['count_preproc_threads'] == 0) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    df['bytes_sent'][
        (df['count_preproc_threads'] == 1) & (df['mode'] == MODE_GOLDEN) & (df['source_dir'] == 'greyscale')].values,
    df['bytes_sent'][
        (df['count_preproc_threads'] == 1) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')].values,
    df['bytes_sent'][
        (df['count_preproc_threads'] == 1) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    df['bytes_sent'][
        (df['count_preproc_threads'] == 2) & (df['mode'] == MODE_GOLDEN) & (df['source_dir'] == 'greyscale')].values,
    df['bytes_sent'][
        (df['count_preproc_threads'] == 2) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')].values,
    df['bytes_sent'][
        (df['count_preproc_threads'] == 2) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')].values,

    # df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['mode'] == MODE_GOLDEN) & (df['source_dir'] == 'greyscale')],
    # df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['mode'] == MODE_SPLINES) & (df['source_dir'] == 'greyscale')],
    # df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['mode'] == MODE_NATURAL) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 0) & (df['source_dir'] == 'ffill')].values,
],
    labels=[
        'g,0,n',

        'g,1,g',
        'g,1,s',
        'g,1,n',

        'g,2,g',
        'g,2,s',
        'g,2,n',

        # 'g,3,g',
        # 'g,3,s',
        # 'g,3,n',

        'ffill,0',
    ],
    whis='range'
)


plt.savefig(f'figures/{RUN}.0.boxwhisker.bytes_sent.png')

plt.clf()
plt.plot(df.index, df['time_taken'])
plt.savefig(f'figures/{RUN}.1.all_times.png')

# ----

plt.clf()
plt.boxplot([
    df['bytes_sent'][(df['count_preproc_threads'] == 0) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 0) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 1) & (df['mode'] == True) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 1) & (df['mode'] == True) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 2) & (df['mode'] == True) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 2) & (df['mode'] == True) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['mode'] == True) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 3) & (df['mode'] == True) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 1) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 1) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 2) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 2) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')]/df['time_taken'][(df['count_preproc_threads'] == 3) & (df['mode'] == False) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 0) & (df['source_dir'] == 'ffill')]/df['time_taken'][(df['count_preproc_threads'] == 0) & (df['source_dir'] == 'ffill')],
],
    labels=[
        'g,0,r',

        'g,1,s',
        'g,2,s',
        'g,3,s',

        'g,1,r',
        'g,2,r',
        'g,3,r',

        'ffill,0',
    ],
    whis='range'
)




plt.savefig(f'figures/{RUN}.0.boxwhisker.mean_upload_speed.png')





plt.clf()
plt.plot(df.index, df['time_taken'])
plt.savefig(f'figures/{RUN}.1.all_times.png')



print()
