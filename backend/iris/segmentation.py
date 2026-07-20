# ---------------------------------------------------------------
# Panoptes — iris segmentation
#
# Finds the pupil (inner) and iris (outer) boundary as circles in
# a grayscale eye image, using the Hough circle transform. This is
# the classic first step of the Daugman iris-recognition pipeline:
# https://en.wikipedia.org/wiki/Iris_recognition
#
# Real hardware would feed this a near-infrared camera frame. Here
# it works on the CASIA-IrisV1 sample images in sample_data/.
# ---------------------------------------------------------------

import cv2
import numpy as np


class SegmentationError(Exception):
    pass


def find_pupil(gray):
    """Pupil is the darkest, roughly-circular region. Hough works
    well on it directly since the pupil/iris edge is high-contrast."""
    blurred = cv2.medianBlur(gray, 7)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
        param1=50, param2=30, minRadius=15, maxRadius=60,
    )
    if circles is None:
        raise SegmentationError("Could not locate pupil boundary")
    # take the most confident (first) circle
    x, y, r = circles[0][0]
    return float(x), float(y), float(r)


def find_iris(gray, pupil_x, pupil_y, pupil_r):
    """Iris outer boundary. Pupil and iris are physiologically
    concentric (same center, near-frontal gaze), so candidates are
    constrained to circles centered close to the pupil's — this
    rules out the many false circles Hough otherwise finds on
    eyelids, lashes, and specular reflections elsewhere in the frame.
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=200,
        param1=40, param2=20,
        minRadius=int(pupil_r + 40), maxRadius=int(pupil_r + 100),
    )

    concentric_max_offset = 12.0  # pixels

    if circles is not None:
        candidates = [
            c for c in circles[0]
            if (c[0] - pupil_x) ** 2 + (c[1] - pupil_y) ** 2 <= concentric_max_offset ** 2
        ]
        if candidates:
            x, y, r = candidates[0]
            return float(x), float(y), float(r)

    # fall back to a fixed proportional estimate, centered on the
    # pupil, rather than trusting an off-center Hough guess
    return pupil_x, pupil_y, pupil_r + 53


def segment_eye(image_path):
    """Returns (pupil_circle, iris_circle, gray_image) where each
    circle is (x, y, r)."""
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise SegmentationError(f"Could not read image: {image_path}")

    px, py, pr = find_pupil(gray)
    ix, iy, ir = find_iris(gray, px, py, pr)

    return (px, py, pr), (ix, iy, ir), gray
