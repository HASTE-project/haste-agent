import os
import time
from PIL import Image
import haste.desktop_agent.benchmarking.benchmarking_config as benchmarking_config
import haste.desktop_agent.flood_fill_preprocessor.flood_fill as flood_fill

filenames_orig = list(filter(lambda f: f.endswith('.png'), os.listdir(benchmarking_config.ORIGINAL_DIR)))

def to_greyscale(input_filename, output_filename):
    t_start = time.time()
    img = Image.open(input_filename).convert('L')
    img.save(output_filename)
    t_end = time.time()
    print(t_end - t_start)


# print(filenames)

def convert_all():
    for filename in filenames_orig:
        original_filename = benchmarking_config.ORIGINAL_DIR + filename
        greyscale_filename = benchmarking_config.GREYSCALE_DIR + filename
        ffill_filename = benchmarking_config.FFILL_DIR + filename

        to_greyscale(original_filename, greyscale_filename)

        flood_fill.convert_file(greyscale_filename, ffill_filename)


if __name__ == '__main__':
    convert_all()
