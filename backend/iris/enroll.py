# ---------------------------------------------------------------
# Panoptes — enrollment demo
#
# Enrolls one reference image per sample subject (holding back a
# second image per subject to verify against later). Templates are
# stored as hex-packed bit strings in enrolled_templates.json —
# separate from the live demo's TinyDB, since this is a standalone
# proof that the real pipeline works, not wired into the polling
# dashboard (there's no camera feeding it yet).
#
# Run: python -m iris.enroll
# ---------------------------------------------------------------

import glob
import json
import os

from .pipeline import encode_image, CODE_SHAPE
from .encoding import code_to_hex

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "enrolled_templates.json")

# fictitious names standing in for the 8 sample subjects
SUBJECT_NAMES = {
    "1": "J. Otieno", "2": "A. Mwangi", "3": "B. Kimani", "4": "C. Njeri",
    "5": "D. Wafula", "6": "E. Kariuki", "7": "F. Achieng", "8": "G. Mutua",
}


def enroll_all():
    templates = {}
    for subject_dir in sorted(glob.glob(os.path.join(SAMPLE_DIR, "*"))):
        subject_id = os.path.basename(subject_dir)
        images = sorted(glob.glob(os.path.join(subject_dir, "*")))
        if not images:
            continue

        # enroll on the first image, hold the rest back for verification
        enroll_image = images[0]
        try:
            code, shape = encode_image(enroll_image)
        except Exception as e:
            print(f"  failed to enroll {enroll_image}: {e}")
            continue

        name = SUBJECT_NAMES.get(subject_id, f"subject-{subject_id}")
        templates[name] = {
            "code_hex": code_to_hex(code),
            "code_length": int(code.size),
            "shape": list(shape),
            "source_image": os.path.basename(enroll_image),
        }
        print(f"Enrolled {name} from {os.path.basename(enroll_image)}")

    with open(TEMPLATES_PATH, "w") as f:
        json.dump(templates, f, indent=2)
    print(f"\nSaved {len(templates)} templates to {TEMPLATES_PATH}")


if __name__ == "__main__":
    enroll_all()
