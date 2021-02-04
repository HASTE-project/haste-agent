import time

import pandas as pd

# Used for the 'golden' baseline mode, not used in the paper in the end. deprecated.
csv_results = None

# csv_results = pd.read_csv(
#     #'/Users/benblamey/projects/haste/vironova-image-compression/results/scanlines-viron_2019_02_04__11_34_55.csv',
#     #'/Users/benblamey/projects/haste/vironova-image-compression/results/thres-viron_2019_02_04__11_34_55.csv',
#     # '/Users/benblamey/projects/haste/vironova-image-compression/results/dark-np.csv',
#     '/Users/benblamey/projects/haste/vironova-image-compression/results/old--viron_2019_02_04__11_34_55.csv',
#     header=None,
#     names=[
#         'filename',
#         'dur_load_image_to_np',
#         'dur_flood_fill',
#         'duration_total',
#         'input_file_size_bytes',
#         'output_file_size_bytes',
#     ],
#     skiprows=1)


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
    print(result)
