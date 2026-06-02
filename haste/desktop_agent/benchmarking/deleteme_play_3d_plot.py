import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# 10 example points in 3D
x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
y = np.array([0, 0.5, 1, 0.8, 0.2, -0.5, -1, -0.8, -0.3, 0])
z = np.array([0, 0.3, 0.8, 1.2, 1.5, 1.3, 1.0, 0.6, 0.2, 0])



# Direction vectorsx
u = np.diff(x)
v = np.diff(y)
w = np.diff(z)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot points
ax.scatter(x, y, z, s=40)

# Plot directed arrows
ax.quiver(
    x[:-1], y[:-1], z[:-1],  # starting points
    u, v, w,                 # direction vectors
    arrow_length_ratio=0.20
)

# Labels
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

plt.show()

