# ---------------------------------------------------------------
# Panoptes — iris encoding
#
# Convolves the normalized iris image with a small bank of 2D Gabor
# kernels (different orientations), then binarizes each response by
# sign — one bit per pixel per kernel. This is a simplified stand-in
# for Daugman's original 2D Gabor phase-quadrant encoding: same
# spirit (texture -> binary code via Gabor response), fewer filters,
# no separate noise mask. Good enough for a prototype; a production
# system would add eyelid/eyelash occlusion masking so those regions
# don't corrupt the match.
# ---------------------------------------------------------------

import cv2
import numpy as np

# a handful of orientations is enough to capture iris texture direction
GABOR_ORIENTATIONS = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
# small lambd relative to ksize -> tuned to fine iris texture, not the
# coarse pupil-to-sclera brightness gradient every eye shares
GABOR_PARAMS = dict(ksize=(9, 9), sigma=2.0, lambd=4.0, gamma=0.5, psi=0)


def build_gabor_bank():
    kernels = []
    for theta in GABOR_ORIENTATIONS:
        k = cv2.getGaborKernel(theta=theta, **GABOR_PARAMS, ktype=cv2.CV_32F)
        k -= k.mean()  # zero the DC component so response sign reflects
                       # local texture, not the kernel's own bias
        kernels.append(k)
    return kernels


_GABOR_BANK = build_gabor_bank()


_CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


def encode_iris(normalized_image):
    """Returns a 1D boolean numpy array — the iris code. Length is
    (radial_res * angular_res * number_of_orientations).

    Applies CLAHE (local contrast normalization) first, since raw
    brightness varies a lot with illumination/camera and would
    otherwise swamp the finer texture differences Gabor is meant
    to pick up.
    """
    equalized = _CLAHE.apply(normalized_image)
    img = equalized.astype(np.float32)
    bits = []
    for kernel in _GABOR_BANK:
        response = cv2.filter2D(img, cv2.CV_32F, kernel)
        bits.append(response > 0)
    code = np.concatenate([b.flatten() for b in bits])
    return code


def code_to_hex(code: np.ndarray) -> str:
    """Pack a boolean array into a hex string for storage."""
    packed = np.packbits(code)
    return packed.tobytes().hex()


def hex_to_code(hex_str: str, length: int) -> np.ndarray:
    packed = np.frombuffer(bytes.fromhex(hex_str), dtype=np.uint8)
    bits = np.unpackbits(packed)[:length]
    return bits.astype(bool)
