from haste.desktop_agent.flood_fill_preprocessor.flood_fill import flood_fill_outer
import numpy as np


def test_flood_fill_1():
    input = np.array([
        [0, 1, 3, 4, 4],
        [1, 5, 3, 4, 4],
        [1, 5, 3, 4, 4],
    ])

    assert input[0,2] == 3

    output = flood_fill_outer(input)
    assert np.array_equal(output, np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]))


def test_flood_fill_2():
    input = np.array([
        [0, 1, 3, 4, 4],
        [1, 5, 35, 4, 4],
        [1, 35, 35, 35, 4],
    ])
    output = flood_fill_outer(input)
    assert np.array_equal(output, np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 35, 0, 0],
        [0, 35, 35, 35, 0]
    ]))


def test_flood_fill_3():
    input = np.array([
        [35, 35, 35, 4, 4],
        [1, 1, 35, 4, 35],
        [1, 1, 3, 4, 4],
        [1, 5, 35, 4, 4],
        [1, 35, 35, 35, 4],
    ])
    output = flood_fill_outer(input)
    assert np.array_equal(output, np.array([
        [35, 35, 35, 0, 0],
        [0, 0, 35, 0, 35],
        [0, 0, 0, 0, 0],
        [0, 0, 35, 0, 0],
        [0, 35, 35, 35, 0]
    ]))
