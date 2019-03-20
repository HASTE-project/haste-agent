import sys
import ben_images.flood_fill
from PIL import Image
import numpy as np
import time
from sys import stdin


def convert_file(input_filepath, output_filepath):
    img = Image.open(input_filepath)
    im_array1 = np.asarray(img)

    result = ben_images.flood_fill.flood_fill_outer(im_array1)

    # to greyscale
    Image.fromarray(result).convert('L').save(output_filepath, format='PNG')

    return output_filepath


if __name__ == '__main__':
    while True:
        input_filepath, output_filepath = input().split(',')

        start = time.time()

        convert_file(input_filepath, output_filepath)

        print(time.time() - start)
