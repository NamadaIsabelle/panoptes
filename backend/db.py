# ---------------------------------------------------------------
# Panoptes — data layer
#
# Uses TinyDB: a pure-Python, document-based (NoSQL) store, backed
# by a single JSON file. It's a drop-in conceptual stand-in for
# MongoDB (from the original proposal) with zero setup — no server
# to install or run, which suits a prototype.
#
# To move to real MongoDB later: swap TinyDB() for a pymongo
# client, and replace .insert()/.all()/.search() calls with the
# equivalent insert_one()/find() calls. The document shapes below
# would stay the same.
# ---------------------------------------------------------------

import time
import uuid
from tinydb import TinyDB, Query

DB_PATH = "panoptes_db.json"

db = TinyDB(DB_PATH)
users_table = db.table("users")
logs_table = db.table("logs")
alerts_table = db.table("alerts")

Q = Query()


# ---------------- Users ----------------

def seed_users(names):
    """Populate the users collection if empty. Each user gets a stub
    'template_id' standing in for a real enrolled iris template."""
    if len(users_table) > 0:
        return
    for name in names:
        users_table.insert({
            "user_id": str(uuid.uuid4())[:8],
            "name": name,
            "template_id": str(uuid.uuid4()),
            "enrolled_at": time.time(),
        })


def all_users():
    return users_table.all()


def random_user():
    import random
    users = users_table.all()
    return random.choice(users) if users else None


# ---------------- Logs ----------------

def add_log(gate_id, user_name, direction, confidence, flagged, flag_reason=None):
    entry = {
        "id": str(uuid.uuid4())[:8],
        "gate_id": gate_id,
        "user": user_name,
        "direction": direction,     # "in" | "out"
        "confidence": confidence,
        "flagged": flagged,
        "flag_reason": flag_reason,
        "timestamp": time.time(),
    }
    logs_table.insert(entry)
    return entry


def recent_logs(limit=40):
    logs = sorted(logs_table.all(), key=lambda r: r["timestamp"], reverse=True)
    return logs[:limit]


def last_log_for_user(user_name):
    matches = logs_table.search(Q.user == user_name)
    if not matches:
        return None
    return sorted(matches, key=lambda r: r["timestamp"], reverse=True)[0]


# ---------------- Alerts ----------------

def add_alert(title, body, gate_id=None, user_name=None):
    entry = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "body": body,
        "gate_id": gate_id,
        "user": user_name,
        "timestamp": time.time(),
    }
    alerts_table.insert(entry)
    return entry


def recent_alerts(limit=20):
    alerts = sorted(alerts_table.all(), key=lambda r: r["timestamp"], reverse=True)
    return alerts[:limit]


# ---------------- Derived state ----------------

def compute_inside_state():
    """Walk the full log history to figure out who's currently inside
    and per-gate counts. Fine for a prototype; for real scale you'd
    maintain this incrementally instead of recomputing each time."""
    logs = sorted(logs_table.all(), key=lambda r: r["timestamp"])
    inside = set()
    per_gate = {}

    for log in logs:
        gate_id = log["gate_id"]
        per_gate.setdefault(gate_id, set())
        if log["direction"] == "in":
            inside.add(log["user"])
            per_gate[gate_id].add(log["user"])
        else:
            inside.discard(log["user"])
            per_gate[gate_id].discard(log["user"])

    return {
        "inside_count": len(inside),
        "inside_users": sorted(inside),
        "per_gate_counts": {g: len(u) for g, u in per_gate.items()},
        "total_scans": len(logs),
    }