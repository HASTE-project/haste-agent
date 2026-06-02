import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

AXIS_LABEL_TRUE_NMSR = "True NMSR (bytes/sec)"
AXIS_LABEL_MESSAGE_INDEX = "Message Arrival Index"

COLOR = 'tab:blue'


def vector_at_angle(v0, v1, angle_deg=20, arrow_length=0.07):
    # Returns a vector that forms `angle_deg` with (v1 - v0), i.e. arrow heads
    d = v1 - v0
    norm_d = np.linalg.norm(d)
    d = d / norm_d

    # choose a non-collinear reference vector
    ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(ref, d)) > 0.9:
        ref = np.array([1.0, 0.0, 0.0])

    arrow_length = min(arrow_length, norm_d * 0.5)

    # get perpendicular direction with cross product
    n = np.cross(d, ref)
    n /= np.linalg.norm(n)

    angle = np.deg2rad(angle_deg)

    return (v1 - arrow_length * (np.cos(angle) * d + np.sin(angle) * n),
            v1 - arrow_length * (np.cos(angle) * d - np.sin(angle) * n))

def arrowhead3d_2(ax, p0, p1, **kw):
    p0 = np.asarray(p0)

    mins = np.array([
        ax.get_xlim3d()[0],
        ax.get_ylim3d()[0],
        ax.get_zlim3d()[0],
    ])
    maxs = np.array([
        ax.get_xlim3d()[1],
        ax.get_ylim3d()[1],
        ax.get_zlim3d()[1],
    ])

    # data -> unit cube
    p0unit = (p0 - mins) / (maxs - mins)
    p1unit = (p1 - mins) / (maxs - mins)

    arrow0unit, arrow1unit = vector_at_angle(p0unit, p1unit)

    # transform back to axis scales
    arrow0 = mins + arrow0unit * (maxs - mins)
    arrow1 = mins + arrow1unit * (maxs - mins)

    ax.plot([p1[0], arrow0[0]],
            [p1[1], arrow0[1]],
            [p1[2], arrow0[2]], **kw)
    ax.plot([p1[0], arrow1[0]],
            [p1[1], arrow1[1]],
            [p1[2], arrow1[2]], **kw)



def plot(all_golden_compressibilities, event_indices, event_times, start_index, end_index, legend):
    plt.clf()


    golden_ratio = []
    indices = []
    times = []

    for index_in_event_array, overall_index in enumerate(event_indices):
        if start_index <= overall_index < end_index and event_times[index_in_event_array] >110:
            indices.append(overall_index)
            golden_ratio.append(all_golden_compressibilities[overall_index])
            times.append(event_times[index_in_event_array])

    assert len(indices) == len(golden_ratio) == len(times)

    # for i, data in enumerate([indices, golden_ratio, times]):
    #     plt.clf()
    #     plt.plot(range(len(data)), data)
    #     plt.savefig(f'3d_helper_plot{i}.png')

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.autoscale(True)
    ax.set_box_aspect([1, 1, 1])

    x = np.array(indices)
    y = np.array(golden_ratio)
    z = np.array(times)

    ax.set_xlabel(AXIS_LABEL_MESSAGE_INDEX, labelpad=11)
    ax.set_ylabel(AXIS_LABEL_TRUE_NMSR, labelpad=13)
    ax.set_zlabel("Processing Timestamp (seconds)", labelpad=11)

    ax.tick_params(axis='x', pad=4)
    ax.tick_params(axis='y', pad=8)
    ax.tick_params(axis='z', pad=4)

    combined = np.column_stack((x, y, z))
    sorted_combined = combined[np.argsort(combined[:, 0])] # sort by message index (col 0)

    # Direction vectors
    u = np.diff(x)
    v = np.diff(y)
    w = np.diff(z)

    ax.plot(sorted_combined[:, 0], sorted_combined[:, 1], sorted_combined[:, 2], color='black', linewidth=0.5, linestyle='--')
    ax.plot(x, y, z, marker="o", color=COLOR)


    ax.legend(legend)

    for i in range(0, len(indices) - 1):
        arrowhead3d_2(ax, (x[i],
                           y[i],
                           z[i]),
                      (x[i+1],
                       y[i+1],
                       z[i+1]),
                      linestyle='-', marker=None, color=COLOR)

    plt.show()


# TODO: need to exclude on the basis of the times as well