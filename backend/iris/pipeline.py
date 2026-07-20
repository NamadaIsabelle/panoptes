# ---------------------------------------------------------------
# Panoptes — full encode pipeline
#
# segment -> normalize -> encode, in one call. This is what a real
# scan (enrollment or verification) would run against a captured
# frame.
# ---------------------------------------------------------------

from .segmentation import segment_eye
from .normalization import normalize_iris
from .encoding import encode_iris, GABOR_ORIENTATIONS

RADIAL_RES = 64
ANGULAR_RES = 512
CODE_SHAPE = (len(GABOR_ORIENTATIONS), RADIAL_RES, ANGULAR_RES)


def encode_image(image_path):
    """Returns (code: bool ndarray, shape) for a given eye image path."""
    pupil_circle, iris_circle, gray = segment_eye(image_path)
    normalized = normalize_iris(gray, pupil_circle, iris_circle, RADIAL_RES, ANGULAR_RES)
    code = encode_iris(normalized)
    return code, CODE_SHAPE
