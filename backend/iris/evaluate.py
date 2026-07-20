# ---------------------------------------------------------------
# Panoptes — pipeline evaluation
#
# Runs every sample image through the pipeline, then reports the
# distribution of genuine-pair (same subject) vs impostor-pair
# (different subject) Hamming distances. This is how you'd sanity
# check the pipeline actually discriminates between people before
# trusting it for anything — and how you'd pick a match threshold.
#
# Run: python -m iris.evaluate
# ---------------------------------------------------------------

import glob
import os
import statistics

from .pipeline import encode_image, CODE_SHAPE
from .matcher import best_rotated_distance

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")


def load_all_codes():
    """Returns {subject_id: [code, code, ...]}"""
    codes_by_subject = {}
    for subject_dir in sorted(glob.glob(os.path.join(SAMPLE_DIR, "*"))):
        subject_id = os.path.basename(subject_dir)
        codes = []
        for image_path in sorted(glob.glob(os.path.join(subject_dir, "*"))):
            try:
                code, _ = encode_image(image_path)
                codes.append(code)
            except Exception as e:
                print(f"  skipped {image_path}: {e}")
        if codes:
            codes_by_subject[subject_id] = codes
    return codes_by_subject


def evaluate():
    print(f"Loading and encoding images from {SAMPLE_DIR} ...")
    codes_by_subject = load_all_codes()
    subjects = list(codes_by_subject.keys())
    print(f"Encoded {sum(len(v) for v in codes_by_subject.values())} images "
          f"across {len(subjects)} subjects.\n")

    genuine_distances = []
    impostor_distances = []

    # genuine: all pairs within the same subject
    for subject, codes in codes_by_subject.items():
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                d = best_rotated_distance(codes[i], codes[j], CODE_SHAPE)
                genuine_distances.append(d)

    # impostor: first image of each subject vs first image of every other subject
    firsts = {s: codes[0] for s, codes in codes_by_subject.items()}
    for i, s1 in enumerate(subjects):
        for s2 in subjects[i + 1:]:
            d = best_rotated_distance(firsts[s1], firsts[s2], CODE_SHAPE)
            impostor_distances.append(d)

    def summarize(name, values):
        print(f"{name}: n={len(values)}  "
              f"mean={statistics.mean(values):.4f}  "
              f"stdev={statistics.pstdev(values):.4f}  "
              f"min={min(values):.4f}  max={max(values):.4f}")

    summarize("Genuine  (same subject)", genuine_distances)
    summarize("Impostor (different subjects)", impostor_distances)

    gap = statistics.mean(impostor_distances) - statistics.mean(genuine_distances)
    print(f"\nMean separation (impostor - genuine): {gap:.4f}")
    print("\nNote: this is a simplified single-scale Gabor encoder on a small\n"
          "sample set, without eyelid/eyelash occlusion masking. The separation\n"
          "above is real but modest — expect meaningfully better accuracy from\n"
          "a full Daugman-style multi-scale complex log-Gabor implementation\n"
          "with proper noise masking, which is a reasonable next iteration.")


if __name__ == "__main__":
    evaluate()
