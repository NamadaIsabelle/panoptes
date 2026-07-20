# ---------------------------------------------------------------
# Panoptes — iris normalization
#
# Unwraps the annular iris region (between the pupil and iris
# circles) into a fixed-size rectangle, using Daugman's "rubber
# sheet" model. This makes the iris comparable across images
# regardless of pupil dilation or the eye's distance from camera —
# every iris gets mapped to the same (angle, radius) grid.
# ---------------------------------------------------------------

import numpy as np


def normalize_iris(gray, pupil_circle, iris_circle, radial_res=64, angular_res=512):
    """Returns a (radial_res x angular_res) normalized iris image.

    Each column is one angular sample (0 to 2*pi around the eye);
    each row is one radial sample between the pupil edge (row 0)
    and the iris edge (last row).
    """
    px, py, pr = pupil_circle
    ix, iy, ir = iris_circle

    thetas = np.linspace(0, 2 * np.pi, angular_res)
    normalized = np.zeros((radial_res, angular_res), dtype=np.uint8)

    h, w = gray.shape

    for col, theta in enumerate(thetas):
        cos_t, sin_t = np.cos(theta), np.sin(theta)

        # pupil boundary point and iris boundary point along this ray
        x_p, y_p = px + pr * cos_t, py + pr * sin_t
        x_i, y_i = ix + ir * cos_t, iy + ir * sin_t

        for row in range(radial_res):
            frac = row / (radial_res - 1)
            x = x_p + frac * (x_i - x_p)
            y = y_p + frac * (y_i - y_p)

            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < w and 0 <= yi < h:
                normalized[row, col] = gray[yi, xi]
            # else leave as 0 — sample fell outside the image bounds

    return normalized
