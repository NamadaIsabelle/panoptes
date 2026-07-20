# Panoptes — Demo Script (~5 minutes)

Quick cheat sheet to glance at while presenting. Bold = say this. Italics = do this.

---

## 1. Open (30 sec)

**"This is Panoptes — a biometric entrance monitoring prototype. It replaces
ID badges with iris scanning, so security checks the person, not a card
they're carrying."**

*Have the dashboard already open at http://localhost:8000, three terminals
running in the background (see [Before you start](#before-you-start)).*

---

## 2. The problem (30 sec)

**"This came out of a real incident during my internship — outsiders got
past ID-badge checkpoints, even with security staff on site, and got into a
restricted building where they tried to start a fire. It was caught in time,
but it showed how little a badge check actually verifies. If it's not tied
to the person, it can be shared, borrowed, or faked."**

---

## 3. The solution, in one line (15 sec)

**"So instead of checking a card, every gate scans your iris directly —
something you can't hand to someone else — logs every entry and exit, and
flags anything that looks off automatically."**

---

## 4. Live demo — the dashboard (1.5 min)

*Point at the running dashboard.*

**"This is the live security view. Six gates, A through F — some
entrance-only, some exit-only, some both, matching a real building layout."**

*Let a scan or two happen — point at a gate pulsing.*

**"Every scan shows up here in real time — who, which gate, which direction,
confidence score. This table's live, it's polling a real backend API every
1.5 seconds, not just animating on its own."**

*Wait for a flagged alert to appear, or point at the Alerts panel.*

**"When something looks suspicious — someone scanning back in too fast, or a
low-confidence match — it gets flagged here automatically. That's a
rule-based anomaly detector running server-side."**

---

## 5. What's actually running under it (1 min)

**"Behind this is a Flask API and a database logging every scan, and
separately, I built and tested a real iris-recognition pipeline — not just
UI, actual computer vision."**

*Optional — if you want to show real terminal output, run this live:*
```powershell
cd backend
py -m iris.verify
```
**"This runs real iris images through the full pipeline — segment the eye,
normalize it, encode it, match it against enrolled templates — and reports
how often it gets the right person."**

*Point at the accuracy line at the bottom of the output.*

**"58.3% top-1 accuracy identifying the right person out of 8 enrolled
users — random guessing would only get 12.5%. So it's picking up real
signal from the iris texture, not noise."**

---

## 6. Be upfront about the gaps (30 sec)

**"I want to be honest about where this stands: the live dashboard you're
watching uses simulated scans right now, since there's no camera hooked up
yet — but the matching pipeline itself is real and tested. It's also
missing things a production system would need, like liveness detection and
occlusion masking around eyelashes — both documented in the README as next
steps, not skipped by accident."**

---

## 7. Close (15 sec)

**"So — working frontend, working backend, and a real, tested biometric
matching pipeline, all version-controlled on GitHub. Happy to answer
questions or dig into any part of it."**

---

## Before you start

Three terminals, in order:

```powershell
# 1 — backend
cd backend
py app.py

# 2 — simulated scan traffic
cd backend
py simulate_traffic.py

# 3 — frontend
cd frontend
py -m http.server 8000
```

Open **http://localhost:8000**, hard-refresh (Ctrl+Shift+R) if it was
already open. If Terminal 1 throws a `JSONDecodeError`, run
`del panoptes_db.json` then `py app.py` again.

## If something breaks mid-demo

- **Dashboard says "Backend offline"** → check Terminal 1 is still running.
- **No scans appearing** → check Terminal 2 (`simulate_traffic.py`) is still
  running; it fires a scan every 2.5s.
- **Teacher asks to see the code** → have `app.py`, `script.js`, and
  `iris/matcher.py` already open in VS Code tabs, ready to switch to.
- **Worst case** → you have the presentation deck and this script; you can
  walk through it without the live system if needed.
