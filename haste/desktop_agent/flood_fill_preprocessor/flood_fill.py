import numpy as np

import time

from PIL import Image

TOLERANCE = 30  # looks reasonable from the histogram
REPLACEMENT_COLOR = 0
TARGET_COLOR = 0


# Flood-fill Scanline implementation.

def _flood_fill_inner(img, M_visited, row_x, col_y, target_color, tolerance, replacement_color):
    # TODO co-ordinates which way round?

    # takes apx. 0.006
    M_img_tol = (img - target_color) < tolerance
    # M_pushed = np.zeros(M_visited.shape, dtype=bool)

    WIDTH = img.shape[1]
    HEIGHT = img.shape[0]

    queue = set()

    M_visited[0, 0] = True
    img[0, 0] = REPLACEMENT_COLOR
    queue.add((0, 0))

    while len(queue) > 0:
        row, col = queue.pop()
        # print('popped')


        for r, c in [
            (row - 1, col),
            (row + 1, col),
            (row, col + 1),
            (row, col - 1)]:
            if r < 0 or c < 0 or r == HEIGHT or c == WIDTH:
                continue
            if M_visited[r, c] or not M_img_tol[r, c]:
                continue
            M_visited[r,c]=True
            img[r,c] = REPLACEMENT_COLOR
            queue.add((r, c))


def flood_fill_outer(im_array1):
    im_array = np.zeros((im_array1.shape[0] + 2, im_array1.shape[1] + 2))
    im_array[1:-1, 1:-1] = im_array1

    # im_array = im_array1.copy()

    visited = np.zeros(im_array.shape, dtype=bool)
    _flood_fill_inner(im_array, visited, 0, 1023, TARGET_COLOR, TOLERANCE, REPLACEMENT_COLOR)

    # remove the border
    im_array2 = im_array[1:-1, 1:-1]
    return im_array2





def convert_file(input_filepath, output_filepath):
    img = Image.open(input_filepath)
    im_array1 = np.asarray(img)

    result = flood_fill_outer(im_array1)

    # to greyscale
    Image.fromarray(result).convert('L').save(output_filepath, format='PNG')

    return output_filepath


if __name__ == '__main__':
    input = np.array([
        [0, 1, 3, 4, 4],
        [1, 5, 3, 4, 4],
        [1, 5, 3, 4, 4],
    ])
    output = flood_fill_outer(input)
    assert np.array_equal(output, np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]))