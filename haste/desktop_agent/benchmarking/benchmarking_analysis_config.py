
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