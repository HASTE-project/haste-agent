import time

import pandas as pd

from haste.desktop_agent.benchmarking.benchmarking_analysis_config import golden_nmsr_csv

dtypes={
    'filename': "string",
    'dur_load_image_to_np': "float64",
    'dur_flood_fill': "float64",
    'duration_total': "float64",
    'input_file_size_bytes': "float64",
    'output_file_size_bytes': "float64",
}
names=[
    'filename',
    'dur_load_image_to_np',
    'dur_flood_fill',
    'duration_total',
    'input_file_size_bytes',
    'output_file_size_bytes',
],

csv_results = pd.read_csv(
    golden_nmsr_csv,
    sep=",",
    header=0)


def get_golden_prio_for_filename(filename):
    # return 0

    start = time.time()
    row_as_series = csv_results.loc[csv_results['filename'] == filename].squeeze()

    # filename,dur_load_image_to_np,dur_flood_fill,duration_total,input_file_size_bytes,output_file_size_bytes

    result = (row_as_series['input_file_size_bytes'] - row_as_series['output_file_size_bytes']) / row_as_series[
        'duration_total']

    # 2019-03-22 15:16:59.223 - Thread-1 - INFO - get_golden_prio_for_filename took 0.0012850761413574219 secs
    # logging.info(f'get_golden_prio_for_filename took {time.time() - start} secs')


    return result


if __name__ == '__main__':
    result = get_golden_prio_for_filename('strm_2019_02_04__11_34_55_vironova_ts_1549276991.6418386.png')
    #print(result)
