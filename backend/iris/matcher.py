# ---------------------------------------------------------------
# Panoptes — iris matching
#
# Compares two iris codes via Hamming distance (fraction of bits
# that differ — 0.0 is a perfect match, 0.5 is what two unrelated
# irises average out to). Also tries small angular shifts of one
# code against the other, since a tilted head rotates the iris
# pattern around the eye — comparing only at zero rotation would
# reject legitimate matches from a tilted scan.
# ---------------------------------------------------------------

import numpy as np

MAX_ROTATION_SHIFT = 8   # columns to try shifting in each direction


def hamming_distance(code_a: np.ndarray, code_b: np.ndarray) -> float:
    if code_a.shape != code_b.shape:
        raise ValueError("Codes must be the same shape to compare")
    return float(np.count_nonzero(code_a != code_b)) / code_a.size


def best_rotated_distance(code_a: np.ndarray, code_b: np.ndarray, shape) -> float:
    """shape = (num_orientations, radial_res, angular_res). Rolls
    code_b along the angular axis and keeps the best (lowest)
    Hamming distance across the shift range."""
    a = code_a.reshape(shape)
    b = code_b.reshape(shape)

    best = 1.0
    for shift in range(-MAX_ROTATION_SHIFT, MAX_ROTATION_SHIFT + 1):
        shifted = np.roll(b, shift, axis=2)
        dist = float(np.count_nonzero(a != shifted)) / a.size
        best = min(best, dist)
    return best


def confidence_from_distance(distance: float) -> int:
    """Maps a Hamming distance to a 0-100 'confidence' score for
    display purposes. ~0.5 (random codes) -> ~0%, 0.0 (identical) -> 100%.
    Real systems report the distance/FAR curve directly rather than a
    single percentage — this is a simplified stand-in for the dashboard."""
    scaled = max(0.0, 1.0 - distance / 0.5)
    return int(round(scaled * 100))
