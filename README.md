Panoptes — Biometric Entrance Monitoring (Prototype)
📖 Overview
Panoptes is a prototype security system for institutions, built around iris-based biometric authentication. Inspired by Panoptes, the many‑eyed giant of Greek myth, the system is designed to track entries/exits and flag anomalies.

Unlike traditional ID badges (which can be shared or copied), Panoptes ties access to something you can’t lend out — your eyes.

⚠️ This is a prototype for demo purposes, not a production security system.

🚀 Features
Biometric Authentication: Iris recognition pipeline (OpenCV-based segmentation, normalization, encoding, matching).

Frontend Dashboard: HTML/CSS/JS live view of gates, logs, and alerts.

Backend API: Flask + TinyDB, simulates traffic and anomaly detection.

Anomaly Detection: Rule-based flags for rapid re-scans and low-confidence matches.

Extensible Design: Future support for voice, facial recognition, fingerprint, and traditional ID verification.

🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript

Backend: Python (Flask), TinyDB

Biometrics: OpenCV iris recognition pipeline

Data: CASIA-IrisV1 sample dataset (56 images, 8 subjects)

📂 Project Structure
Code
panoptes/
├── frontend/         # Dashboard (HTML/CSS/JS)
└── backend/          # Flask API + Iris pipeline
    ├── app.py
    ├── simulate_traffic.py
    ├── anomaly.py
    ├── iris/         # Segmentation, normalization, encoding, matching
▶️ Running the Demo
Requires Python 3.10+.

Terminal 1 — API

bash
cd backend
pip install -r requirements.txt
python app.py
Terminal 2 — Simulated Scanner Traffic

bash
cd backend
python simulate_traffic.py
Terminal 3 — Dashboard

bash
cd frontend
python -m http.server 8000
Open http://localhost:8000 in your browser.

📊 Results (Prototype Evaluation)
Genuine-pair mean Hamming distance: 0.476

Impostor-pair mean Hamming distance: 0.488

Top-1 identification accuracy: 58.3% (vs. 12.5% random baseline)

⚠️ Limitations
Mocked matching for demo traffic

No liveness detection

No API authentication

Plaintext JSON storage (TinyDB)

Prototype only — not suitable for production

🗺️ Roadmap
Wire real iris pipeline into API

Add occlusion masking + advanced encoding

Scale TinyDB → MongoDB

Entrance/camera placement simulation

WebSocket push for real-time updates

🏆 Credits
Developed by Isabela Risper Namada

LinkedIn

GitHub
