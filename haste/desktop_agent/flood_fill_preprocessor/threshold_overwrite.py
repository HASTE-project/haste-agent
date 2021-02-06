import sys
import time
from PIL import Image

import numpy as np


TOLERANCE = 30  # looks reasonable from the histogram
REPLACEMENT_COLOR = 0
TARGET_COLOR = 0

def flood_fill_outer(im_array):
    im_array = im_array.copy()
    im_array[im_array < TOLERANCE] = 0
    return im_array


if __name__ == '__main__':
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    # input_filename = IMAGE_DIR_ROOT + 'gen/greyscale/' + filename
    # output_filename = IMAGE_DIR_ROOT + 'gen/thres/' + filename


    img = Image.open(input_filename)
    im_array1 = np.asarray(img)

    t_startb = time.time()

    result = flood_fill_outer(im_array1)

    t_endb = time.time()

    # Save as a greyscale image:
    Image.fromarray(result).convert('L').save(output_filename)

