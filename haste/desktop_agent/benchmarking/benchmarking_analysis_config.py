import os


# Note, grepped file is the extraction of the lines which contain the makespans (i.e. when the queue is empty.) from the original log.
# There will be total num_runs * num_configs lines.
# grep Queue_is_empty xxxx.log > grepped.txt

def get_run_streamid_tag_filename_grepped():
    run, stream_id, tag = '11_fri_am','benchmarking', 'tag'
    return (run,
            stream_id,
            tag,
            f'logs/{run}/agent_log_{stream_id}_{tag}.log',
            f'logs/{run}/grepped.txt')

# 'offline' NMSR values. Not needed to run the benchmarking. Used in some of the plots only.
golden_nmsr_csv = os.path.expanduser('~/Documents/_RESEARCH_AND_LEARNING/p-message-size-aware/code-message-size-aware/vironova-image-compression/results/viron_2019_02_04__11_34_55.csv')
