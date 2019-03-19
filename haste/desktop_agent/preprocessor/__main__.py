import sys
import ben_images.flood_fill
from PIL import Image
import numpy as np

input_filepath = sys.argv[1]
output_filepath = sys.argv[2]

img = Image.open(input_filepath)
im_array1 = np.asarray(img)

result = ben_images.flood_fill.flood_fill_outer(im_array1)

# to greyscale
Image.fromarray(result).convert('L').save(output_filepath, format='PNG')
