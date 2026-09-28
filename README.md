Panoptes — Biometric Authentication System (Prototype)
📖 Overview
Panoptes is a prototype biometric entrance monitoring system for institutions. Inspired by Panoptes, the many‑eyed giant of Greek myth, it is designed to track entries/exits and flag anomalies.

Unlike traditional ID badges (which can be shared or copied), Panoptes integrates multiple authentication options — iris recognition, facial recognition, voice, fingerprint, and traditional ID verification — giving users flexibility based on comfort and availability.

⚠️ This is a prototype for demo purposes, not a production security system.

🚀 Features
Biometric Authentication: Iris, facial, voice, fingerprint, plus fallback ID verification.

Frontend Dashboard: HTML/CSS/JS live view of gates, logs, and alerts.

Backend API: Flask + TinyDB, simulates traffic and anomaly detection.

Anomaly Detection: Rule-based flags for rapid re-scans and low-confidence matches.

Extensible Design: Modular pipeline to add or swap biometric methods.

🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript

Backend: Python (Flask), TinyDB

Biometrics: OpenCV (iris, facial), audio processing (voice), fingerprint matching pipeline

Data: CASIA-IrisV1 + sample datasets for other modalities

📊 Results (Prototype Evaluation)
Demonstrated iris recognition pipeline with measurable signal.

Modular design allows integration of additional biometric methods.

⚠️ Limitations
Mocked matching for demo traffic.

No liveness detection.

No API authentication.

Plaintext JSON storage (TinyDB).

Prototype only — not suitable for production.

🗺️ Roadmap
Wire real biometric pipelines (voice, facial, fingerprint) into API.

Add occlusion masking + advanced encoding for iris.

Scale TinyDB → MongoDB.

Entrance/camera placement simulation.

WebSocket push for real-time updates.

🏆 Credits
Developed by Isabela Risper Namada

LinkedIn

GitHub
