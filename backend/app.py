# ---------------------------------------------------------------
# Panoptes — backend API
#
# Run with:  python app.py
# Then:      curl -X POST http://localhost:5000/api/scan -d '{"gate_id":"A"}' -H "Content-Type: application/json"
#
# Endpoints:
#   GET  /api/gates            -> gate configuration
#   GET  /api/state            -> who's inside, per-gate counts, scan total
#   GET  /api/logs?limit=40    -> recent access log entries
#   GET  /api/alerts?limit=20  -> recent anomaly alerts
#   POST /api/scan             -> trigger one scan at a gate {"gate_id": "A"}
# ---------------------------------------------------------------

from flask import Flask, jsonify, request
from flask_cors import CORS

import db
from config import GATES, GATE_IDS
from matching import match_iris_mock
from anomaly import check_anomaly

app = Flask(__name__)
CORS(app)  # allow the frontend (served separately) to call this API

SEED_NAMES = [
    "J. Otieno", "A. Mwangi", "B. Kimani", "C. Njeri", "D. Wafula",
    "E. Kariuki", "F. Achieng", "G. Mutua", "H. Wanjiru", "I. Odhiambo",
]


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/gates")
def gates():
    return jsonify(GATES)


@app.route("/api/state")
def state():
    return jsonify(db.compute_inside_state())


@app.route("/api/logs")
def logs():
    limit = request.args.get("limit", default=40, type=int)
    return jsonify(db.recent_logs(limit))


@app.route("/api/alerts")
def alerts():
    limit = request.args.get("limit", default=20, type=int)
    return jsonify(db.recent_alerts(limit))


@app.route("/api/scan", methods=["POST"])
def scan():
    """
    Trigger a scan at a gate. Body: {"gate_id": "A"}

    In a real deployment this endpoint would receive an image (or a
    feature vector) captured at the gate. Here it mocks a match
    against the enrolled user set instead, since there's no camera
    in the loop for the demo.
    """
    payload = request.get_json(silent=True) or {}
    gate_id = payload.get("gate_id")

    if gate_id not in GATE_IDS:
        return jsonify({"error": f"unknown gate_id '{gate_id}'"}), 400

    gate = next(g for g in GATES if g["id"] == gate_id)

    user, confidence = match_iris_mock(db.all_users())
    if user is None:
        return jsonify({"error": "no enrolled users to match against"}), 500

    # direction depends on gate type + whether this user is currently inside
    inside_state = db.compute_inside_state()
    currently_inside = user["name"] in inside_state["inside_users"]

    if gate["type"] == "entrance":
        direction = "in"
    elif gate["type"] == "exit":
        direction = "out"
    else:
        direction = "out" if currently_inside else "in"

    last_log = db.last_log_for_user(user["name"])
    flagged, reason = check_anomaly(user["name"], gate["name"], confidence, last_log)

    log_entry = db.add_log(gate_id, user["name"], direction, confidence, flagged, reason)

    if flagged:
        db.add_alert("Suspicious pattern", reason, gate_id=gate_id, user_name=user["name"])

    return jsonify({
        "gate_id": gate_id,
        "gate_name": gate["name"],
        "user": user["name"],
        "direction": direction,
        "confidence": confidence,
        "flagged": flagged,
        "flag_reason": reason,
        "log_id": log_entry["id"],
    })


if __name__ == "__main__":
    db.seed_users(SEED_NAMES)
    app.run(debug=True, port=5000)
