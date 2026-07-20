# ---------------------------------------------------------------
# Panoptes — site configuration
# Keep this in sync with frontend/config.js. Same gate IDs/types
# so events line up on both sides.
# ---------------------------------------------------------------

GATES = [
    {"id": "A", "name": "Gate A", "type": "both"},       # entrance + exit
    {"id": "B", "name": "Gate B", "type": "entrance"},
    {"id": "C", "name": "Gate C", "type": "exit"},
    {"id": "D", "name": "Gate D", "type": "both"},
    {"id": "E", "name": "Gate E", "type": "entrance"},
    {"id": "F", "name": "Gate F", "type": "both"},
]

GATE_IDS = {g["id"] for g in GATES}

# Anomaly detection thresholds
RAPID_REENTRY_SECONDS = 8       # two scans for same user within this window = suspicious
LOW_CONFIDENCE_THRESHOLD = 93   # accepted match below this confidence gets flagged
