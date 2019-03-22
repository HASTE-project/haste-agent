import matplotlib.pyplot as plt

LOG_FILE_NAME = '2019_03_22__11_40_21_trash'

timestamps = []
pre_processeds = []
not_pre_processeds = []
total = []

lines = []

with open('../../logs/log_%s.log' % LOG_FILE_NAME, 'r') as f:
    for line in f:
        if 'PLOT' not in line:
            continue
        lines.append(line)

for line in lines:
    lines.sort()
    comp = line.split('-')

    timestamp = float(comp[6])
    pre_processed = float(comp[7])
    not_pre_processed = float(comp[8])

    timestamps.append(timestamp)
    pre_processeds.append(pre_processed)
    not_pre_processeds.append(not_pre_processed)
    total.append(pre_processed+not_pre_processed)


plt.clf()
plt.scatter(timestamps, pre_processeds, label='preprocessed')
plt.scatter(timestamps, total, label='total')
plt.xlabel('time')
plt.ylabel('queue length')
plt.legend()
plt.show()
plt.savefig('../../figures/0.' + LOG_FILE_NAME + '.png')