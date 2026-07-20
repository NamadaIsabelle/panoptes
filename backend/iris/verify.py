# ---------------------------------------------------------------
# Panoptes — verification demo
#
# Takes the images NOT used for enrollment (everything after the
# first per subject) and matches each against every enrolled
# template, reporting the best match and whether it was correct.
# This is the end-to-end proof: real images in, real (identify /
# reject) decisions out.
#
# Run: python -m iris.enroll     (first, if you haven't already)
# Run: python -m iris.verify
# ---------------------------------------------------------------

import glob
import json
import os

from .pipeline import encode_image
from .encoding import hex_to_code
from .matcher import best_rotated_distance, confidence_from_distance
from .enroll import SAMPLE_DIR, TEMPLATES_PATH, SUBJECT_NAMES

MATCH_THRESHOLD = 0.480  # picked from evaluate.py's genuine/impostor distributions —
                          # genuine mean ~0.476, impostor mean ~0.488, considerable overlap


def load_templates():
    with open(TEMPLATES_PATH) as f:
        raw = json.load(f)
    templates = {}
    for name, entry in raw.items():
        code = hex_to_code(entry["code_hex"], entry["code_length"])
        templates[name] = (code, tuple(entry["shape"]))
    return templates


def identify(image_path, templates):
    """Returns (best_name, confidence, distance, accepted:bool)."""
    query_code, query_shape = encode_image(image_path)

    best_name, best_distance = None, 1.0
    for name, (template_code, shape) in templates.items():
        d = best_rotated_distance(query_code, template_code, shape)
        if d < best_distance:
            best_name, best_distance = name, d

    accepted = best_distance < MATCH_THRESHOLD
    confidence = confidence_from_distance(best_distance)
    return best_name, confidence, best_distance, accepted


def run_verification():
    templates = load_templates()
    if not templates:
        print("No enrolled templates found — run `python -m iris.enroll` first.")
        return

    top1_correct, accept_correct, total = 0, 0, 0

    for subject_dir in sorted(glob.glob(os.path.join(SAMPLE_DIR, "*"))):
        subject_id = os.path.basename(subject_dir)
        true_name = SUBJECT_NAMES.get(subject_id, f"subject-{subject_id}")
        images = sorted(glob.glob(os.path.join(subject_dir, "*")))[1:]

        for image_path in images:
            try:
                best_name, confidence, distance, accepted = identify(image_path, templates)
            except Exception as e:
                print(f"  {os.path.basename(image_path)}: FAILED ({e})")
                continue

            total += 1
            is_top1_correct = best_name == true_name
            top1_correct += is_top1_correct
            accept_correct += accepted and is_top1_correct

            status = "OK " if is_top1_correct else "ERR"
            print(f"[{status}] {os.path.basename(image_path):16s} true={true_name:12s} "
                  f"best_match={best_name or '(none)':12s} conf={confidence:3d}%  "
                  f"dist={distance:.4f}  {'ACCEPTED' if accepted else 'rejected'}")

    print(f"\nTop-1 identification accuracy: {top1_correct}/{total} "
          f"({100*top1_correct/total:.1f}%) - nearest enrolled template matches "
          f"the true subject, regardless of accept/reject threshold.")
    print(f"(random-chance baseline for {len(templates)} enrolled subjects: "
          f"{100/len(templates):.1f}%)")
    print(f"\nCorrectly identified AND accepted at threshold {MATCH_THRESHOLD}: "
          f"{accept_correct}/{total} ({100*accept_correct/total:.1f}%)")


if __name__ == "__main__":
    run_verification()
