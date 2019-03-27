with open('haste/desktop_agent/benchmarking/logs/agent_log_2019_03_23__14_10_13_trash.log', 'r') as f:
    lines = f.readlines()

lines_joined = '\n'.join(lines)

import os

filenames = os.listdir('/Users/benblamey/projects/haste/haste-desktop-agent-images/target/')


for filename in filenames:
    if filename not in lines_joined:
        print(filename)
    if f"pushed event: <FileCreatedEvent: src_path='/Users/benblamey/projects/haste/haste-desktop-agent-images/target/{filename}" not in lines_joined:
        print(filename)
