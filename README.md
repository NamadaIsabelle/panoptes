# Panoptes

Biometric (iris-based) entrance monitoring — prototype built for a school/institution security project.

> *Panoptes — the many-eyed giant of Greek myth, always watching. The name fits a system built to track who enters and exits, and flag anything that looks wrong.*

## Why this exists

Traditional ID-badge security at institutions is fraud-prone — badges can be shared, copied, or handed to an outsider. Panoptes replaces that with iris-based biometric authentication at each entrance: you can't lend someone your eyes the way you can lend them a badge.

This is a **prototype for demo purposes**, not a production security system. See [Limitations](#limitations--known-gaps) below.

## How it's built

```
panoptes/
├── frontend/         Live dashboard — gates, access log, alerts
│   ├── index.html
│   ├── style.css
│   ├── config.js
│   └── script.js
└── backend/          Flask API + data layer
    ├── app.py
    ├── db.py
    ├── config.py
    ├── matching.py
    ├── anomaly.py
    ├── simulate_traffic.py
    └── requirements.txt
```

**Backend** — Flask API backed by TinyDB (a document-based, NoSQL-style store — a zero-setup stand-in for MongoDB). Handles scan events, logs, alerts, and derived state (who's currently inside, per-gate counts).

**Frontend** — Plain HTML/CSS/JS dashboard, no build step. Polls the backend every 1.5s and renders live gate status, the access log, and any anomaly alerts.

**Matching** — currently mocked (`backend/matching.py` picks a random enrolled user rather than doing real iris comparison), since there's no camera/hardware in this demo. The file documents the real approach (segment → encode → compare against enrolled templates) for whoever picks this up next.

**Anomaly detection** — rule-based, not ML (`backend/anomaly.py`): flags rapid re-scans and low-confidence accepted matches. Reasonable for a prototype; a trained model would need more real log data than a demo produces.

**Gate config** — `backend/config.py` is the single source of truth for gate IDs, names, and types (`entrance` / `exit` / `both`). The frontend fetches this from the API rather than duplicating it.

## Running it

Needs Python 3.10+.

```powershell
# Terminal 1 — API
cd backend
py -m pip install -r requirements.txt
py app.py

# Terminal 2 — simulated scanner traffic (stands in for real hardware)
cd backend
py simulate_traffic.py

# Terminal 3 — serve the dashboard (don't open index.html directly)
cd frontend
py -m http.server 8000
```

Then open **http://localhost:8000**.

> **Windows note:** if `python`/`pip` aren't recognized, use `py` and `py -m pip` instead — see [python.org](https://www.python.org/downloads/) if Python isn't installed at all, and make sure "Add to PATH" is checked during install.

## API reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/gates` | Gate configuration |
| GET | `/api/state` | Who's inside, per-gate counts, total scans |
| GET | `/api/logs?limit=40` | Recent access log entries |
| GET | `/api/alerts?limit=20` | Recent anomaly alerts |
| POST | `/api/scan` | Trigger a scan: `{"gate_id": "A"}` |

## Limitations & known gaps

- **No real biometric matching** — `matching.py` is a random mock. Real iris recognition (segmentation, encoding, comparison against enrolled templates) is unbuilt.
- **No liveness detection** — a real deployment would need protection against photo/prosthetic spoofing. Out of scope for this prototype.
- **No authentication on the API itself** — anyone who can reach the Flask server can call any endpoint. Fine for a local demo, not fine for anything real.
- **Data is stored as plaintext JSON** (TinyDB) — a real system would need encryption at rest and a proper access-control policy, especially given this is biometric data.
- **Prototype only, not deployed** — built for demonstration, per the original project scope.

## Roadmap

- [ ] Real iris matching pipeline (OpenCV, Kaggle iris dataset for mock enrollment data)
- [ ] Swap TinyDB → MongoDB if this needs to scale past a demo
- [ ] AutoCAD-based entrance/camera placement simulation
- [ ] WebSocket push instead of polling, if latency becomes noticeable
