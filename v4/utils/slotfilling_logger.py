import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
LOG_FILE = os.path.join(LOG_DIR, 'slotfilling_log.jsonl')

os.makedirs(LOG_DIR, exist_ok=True)

def log_slotfilling_event(event: dict):
    event = dict(event)  # Defensive copy
    event['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n') 