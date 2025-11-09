#CVS filea kaydediyor sonrada siliyor 

import csv
import os
import atexit
import signal

SESSION_CSV = "session_messages.csv"

def _cleanup_csv() -> None:
    try:
        if os.path.exists(SESSION_CSV):
            os.remove(SESSION_CSV)
    except Exception:
        pass

atexit.register(_cleanup_csv)

def _signal_handler(signum, frame):
    _cleanup_csv()
    os._exit(0)

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

def open_csv_writer():
    is_new = not os.path.exists(SESSION_CSV)
    f = open(SESSION_CSV, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if is_new:
        w.writerow([
            "timestamp", "message_id", "chunk_index", "attempt", "status", "symbol", "note", "loss_prob"
        ])
        f.flush()
    return w, f
