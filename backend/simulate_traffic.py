# ---------------------------------------------------------------
# Panoptes — traffic simulator
#
# Stands in for real scanners: hits POST /api/scan on a timer, at a
# random gate, so there's something to look at during a demo without
# any hardware attached. Run this alongside app.py:
#
#   python app.py                  (terminal 1)
#   python simulate_traffic.py     (terminal 2)
# ---------------------------------------------------------------

import random
import time
import requests

from config import GATE_IDS

API_URL = "http://localhost:5000/api/scan"
INTERVAL_SECONDS = 2.5


def run():
    print(f"Simulating scan traffic against {API_URL} every {INTERVAL_SECONDS}s. Ctrl+C to stop.")
    gate_ids = list(GATE_IDS)
    while True:
        gate_id = random.choice(gate_ids)
        try:
            resp = requests.post(API_URL, json={"gate_id": gate_id}, timeout=3)
            resp.raise_for_status()
            data = resp.json()
            flag = " ⚠ FLAGGED" if data["flagged"] else ""
            print(f"[{gate_id}] {data['user']} -> {data['direction'].upper()} "
                  f"({data['confidence']}%){flag}")
        except requests.RequestException as e:
            print(f"scan failed: {e}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()