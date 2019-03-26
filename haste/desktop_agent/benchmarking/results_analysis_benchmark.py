import pandas as pd

from haste.desktop_agent.benchmarking.__main__ import CONFIGS
import matplotlib.pyplot as plt

RUN = '4_tues_pm_home_200_images'

# grep Queue_is_empty *.log > grepped.txt

# agent_log_2019_03_24__01_07_06_trash.log:2019-03-24 01:12:22.243 - AGENT - MainThread - INFO - Queue_is_empty. Duration since first event: 311.5138850212097 - total_bytes_sent: 315629743

with open(f'logs/{RUN}/grepped.txt') as f:
    lines = f.readlines()
    lines.sort()  # timestamp of each run at the start of the filename
    # assert len(lines) == 25

    count_preproc_threads = []
    splines_enabled = []
    source_dir = []
    time_taken = []
    bytes_sent = []

    for i, line in enumerate(lines):
        config = CONFIGS[i % len(CONFIGS)]
        print(config)
        print(line)
        print('---')

        count_preproc_threads.append(config[0])
        splines_enabled.append(config[2])
        source_dir.append(config[1].split('/')[-2])
        time_taken.append(float(line.split(' ')[-4]))
        bytes_sent.append(float(line.split(' ')[-1]))


data = {
    'count_preproc_threads': count_preproc_threads,
    'splines_enabled': splines_enabled,
    'source_dir': source_dir,
    'time_taken': time_taken,
    'bytes_sent': bytes_sent
}
df = pd.DataFrame(data,
                  columns=['count_preproc_threads', 'splines_enabled', 'source_dir', 'time_taken', 'bytes_sent'])

plt.clf()
plt.boxplot([
    df['time_taken'][(df['count_preproc_threads'] == 0) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],

    df['time_taken'][(df['count_preproc_threads'] == 1) & (df['splines_enabled'] == True) & (df['source_dir'] == 'greyscale')],
    df['time_taken'][(df['count_preproc_threads'] == 2) & (df['splines_enabled'] == True) & (df['source_dir'] == 'greyscale')],
    df['time_taken'][(df['count_preproc_threads'] == 3) & (df['splines_enabled'] == True) & (df['source_dir'] == 'greyscale')],

    df['time_taken'][(df['count_preproc_threads'] == 1) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],
    df['time_taken'][(df['count_preproc_threads'] == 2) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],
    df['time_taken'][(df['count_preproc_threads'] == 3) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],

    df['time_taken'][(df['count_preproc_threads'] == 0) & (df['source_dir'] == 'ffill')],
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
    ]
)
plt.savefig(f'figures/{RUN}.0.boxwhisker.time_taken.png')

plt.clf()
plt.boxplot([
    df['bytes_sent'][(df['count_preproc_threads'] == 0) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 1) & (df['splines_enabled'] == True) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 2) & (df['splines_enabled'] == True) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['splines_enabled'] == True) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 1) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 2) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],
    df['bytes_sent'][(df['count_preproc_threads'] == 3) & (df['splines_enabled'] == False) & (df['source_dir'] == 'greyscale')],

    df['bytes_sent'][(df['count_preproc_threads'] == 0) & (df['source_dir'] == 'ffill')],
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
    ]
)
plt.savefig(f'figures/{RUN}.0.boxwhisker.bytes_sent.png')

plt.clf()
plt.plot(df.index, df['time_taken'])
plt.savefig(f'figures/{RUN}.1.all_times.png')

print()
