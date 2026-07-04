# ---------------------------------------------------------------
# Panoptes — anomaly detection
#
# Rule-based on purpose: for a 10-day prototype, hand-written rules
# over the log history are realistic and explainable. A trained
# model (e.g. isolation forest over entry/exit frequency features)
# is a reasonable upgrade later, once there's enough real log data
# to train on — not before.
# ---------------------------------------------------------------

import time
from config import RAPID_REENTRY_SECONDS, LOW_CONFIDENCE_THRESHOLD


def check_anomaly(user_name, gate_name, confidence, last_log):
    """Returns (flagged: bool, reason: str | None) for a scan that's
    about to be logged. `last_log` is that user's previous log entry,
    or None if this is their first scan."""

    # Rule 1: low-confidence match still accepted
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return True, (
            f"Low-confidence match ({confidence}%) accepted at {gate_name} "
            f"— below the {LOW_CONFIDENCE_THRESHOLD}% review threshold."
        )

    # Rule 2: rapid re-entry — same user scanning again within a few
    # seconds, which a legitimate walk-through wouldn't produce.
    if last_log is not None:
        elapsed = time.time() - last_log["timestamp"]
        if elapsed < RAPID_REENTRY_SECONDS:
            return True, (
                f"Rapid re-scan for {user_name} — only {elapsed:.1f}s since "
                f"their last scan at {last_log['gate_id']}."
            )

    return False, None