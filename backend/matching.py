# ---------------------------------------------------------------
# Panoptes — biometric matching
#
# This is a MOCK matcher: no real iris images come through the demo,
# so it picks a random enrolled user and a plausible confidence
# score. It exists to define the interface the rest of the system
# talks to, so the mock can be swapped for real matching later
# without touching app.py, db.py, or the frontend.
#
# Real version sketch (not implemented here — needs OpenCV, a
# camera, and enrolled reference templates):
#
#   def match_iris(image):
#       segmented = segment_iris(image)              # locate iris/pupil boundary
#       encoded   = encode_iris(segmented)             # e.g. Gabor wavelets / Daugman's method
#       best_user, best_score = None, 0
#       for user in enrolled_users():
#           score = compare(encoded, user.template)    # e.g. Hamming distance -> similarity %
#           if score > best_score:
#               best_user, best_score = user, score
#       return best_user, best_score
#
# ---------------------------------------------------------------

import random


def match_iris_mock(candidate_users):
    """Simulates a scan attempt against the enrolled user set.
    Returns (user_dict, confidence:int 0-100)."""
    if not candidate_users:
        return None, 0
    user = random.choice(candidate_users)
    confidence = random.randint(88, 99)
    return user, confidence
