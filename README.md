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
    ├── requirements.txt
    └── iris/                     Real OpenCV iris matching pipeline
        ├── segmentation.py
        ├── normalization.py
        ├── encoding.py
        ├── matcher.py
        ├── pipeline.py
        ├── enroll.py
        ├── verify.py
        ├── evaluate.py
        └── sample_data/           56 sample images, 8 subjects (CASIA-IrisV1)
```

**Backend** — Flask API backed by TinyDB (a document-based, NoSQL-style store — a zero-setup stand-in for MongoDB). Handles scan events, logs, alerts, and derived state (who's currently inside, per-gate counts).

**Frontend** — Plain HTML/CSS/JS dashboard, no build step. Polls the backend every 1.5s and renders live gate status, the access log, and any anomaly alerts.

**Matching** — two layers, deliberately kept separate:
- *Live demo* (`backend/matching.py`): mocked — picks a random enrolled user, since `simulate_traffic.py` has no real images to feed it and the dashboard needs continuous fake traffic to demo against.
- *Real pipeline* (`backend/iris/`): an actual OpenCV-based iris recognition implementation — segmentation (Hough circle detection), Daugman rubber-sheet normalization, Gabor-filter texture encoding, and Hamming-distance matching with rotation tolerance. Tested against 56 real iris images (CASIA-IrisV1 sample, 8 subjects) — see [Iris matching pipeline](#iris-matching-pipeline) below. Not yet wired into the live API; runnable standalone to prove it works.

**Anomaly detection** — rule-based, not ML (`backend/anomaly.py`): flags rapid re-scans and low-confidence accepted matches. Reasonable for a prototype; a trained model would need more real log data than a demo produces.

**Gate config** — `backend/config.py` is the single source of truth for gate IDs, names, and types (`entrance` / `exit` / `both`). The frontend fetches this from the API rather than duplicating it.

## Iris matching pipeline

`backend/iris/` is a real (not mocked) iris recognition implementation, built and tested against actual iris images rather than assumed to work.

**Pipeline:** `segmentation.py` (locate pupil/iris boundaries via Hough circles, constrained to be concentric) → `normalization.py` (Daugman rubber-sheet unwrap to a fixed 64×512 grid) → `encoding.py` (4-orientation Gabor filter bank, CLAHE contrast normalization, sign-binarized into an iris code) → `matcher.py` (Hamming distance with ±8 column rotation search for head-tilt tolerance).

**Try it yourself:**
```powershell
cd backend
py -m iris.enroll      # enrolls 1 reference image per sample subject
py -m iris.verify       # matches the held-out images against those templates
py -m iris.evaluate     # reports genuine vs. impostor distance distributions
```

**Honest results**, evaluated on 56 sample images (8 subjects, CASIA-IrisV1):
- Genuine-pair (same eye) mean Hamming distance: **0.476** (stdev 0.014)
- Impostor-pair (different eyes) mean Hamming distance: **0.488** (stdev 0.004)
- Top-1 identification accuracy: **58.3%** (vs. 12.5% random-chance baseline for 8 subjects)

That's a real, measurable signal — nowhere near production biometric accuracy, but far better than chance, and an honest result to report rather than an inflated one. The two distance distributions overlap considerably, which is why accept/reject thresholding is much less reliable than top-1 identification here.

**What would improve this** (in rough order of impact): eyelid/eyelash occlusion masking (currently none — lashes corrupt part of every code), a proper 2D complex log-Gabor phase-quadrant encoding instead of a simplified real-valued sign encoding, multiple enrollment images per user averaged into one template, and a larger sample set. All reasonable next steps, not done here given the prototype's scope and timeline.

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

- [ ] Wire the real iris pipeline into `/api/scan` (needs a camera or a way to feed it real captured images)
- [ ] Occlusion masking + multi-scale encoding to improve match accuracy
- [ ] Swap TinyDB → MongoDB if this needs to scale past a demo
- [ ] AutoCAD-based entrance/camera placement simulation
- [ ] WebSocket push instead of polling, if latency becomes noticeable
