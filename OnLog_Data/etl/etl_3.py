import json
import subprocess
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/mnt/d/onlog_data")
STATE_FILE = Path("etl_state.json")

START = "2025-10-01"
END   = "2025-10-03"


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"done": []}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def main():
    state = load_state()
    done = set(state["done"])

    files = sorted(DATA_DIR.glob("F*_*.sqlite"))

    for f in files:
        if f.name in done:
            continue

        log(f"RUN {f.name}")

        proc = subprocess.run(
            [
                "python3",
                "etl_worker_copy.py",
                "--sqlite", str(f),
                "--start", START,
                "--end", END
            ]
        )

        if proc.returncode == 0:
            log(f"SUCCESS {f.name}")
            done.add(f.name)
            save_state({"done": list(done)})
        else:
            log(f"FAILED {f.name} (exit={proc.returncode})")
            break   # 실패 시 중단 (원하면 continue 가능)

    log("ALL POSSIBLE FILES PROCESSED")


if __name__ == "__main__":
    main()
