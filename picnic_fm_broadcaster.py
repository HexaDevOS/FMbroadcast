# picnic_fm_broadcaster.py
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set
import requests
from dotenv import load_dotenv

from si4713_ctl import Si4713Controller

load_dotenv()

API_BASE = os.getenv("API_BASE", "https://www.picnicapp.link/api/v1/fm/")
BEARER = os.getenv("PICNIC_BEARER")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SEC", "20"))
PAGE_LIMIT = int(os.getenv("PAGE_LIMIT", "10"))

FM_FREQ = float(os.getenv("FM_FREQUENCY_MHZ", "100.1"))
FM_PWR = int(os.getenv("FM_TX_POWER", "110"))
ALSA_DEVICE = os.getenv("ALSA_DEVICE", "default")
TTS_VOICE = os.getenv("TTS_VOICE", "en")
TTS_RATE = os.getenv("TTS_RATE", "175")

HEADERS = {"Authorization": f"Bearer {BEARER}"} if BEARER else {}

DATA_DIR = Path.home() / "picnic-fm" / "out"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SEEN_FILE = DATA_DIR / "seen.json"

def espeak_to_wav(text: str, out_path: Path):
    cmd = ["espeak-ng", "-v", TTS_VOICE, "-s", str(TTS_RATE), "-w", str(out_path), text]
    subprocess.run(cmd, check=True)

def play_wav(path: Path):
    cmd = ["aplay", "-D", ALSA_DEVICE, str(path)]
    subprocess.run(cmd, check=True)

def get_all_groups() -> List[Dict]:
    out = []
    page = 1
    while True:
        url = f"{API_BASE}get-all-groups?page={page}&limit={PAGE_LIMIT}&q="
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        j = r.json()
        data = j.get("data", {})
        out.extend(data.get("data", []))
        nxt = data.get("pagination", {}).get("nextPage")
        if not nxt:
            break
        page = nxt
    return out

def get_messages(group_id: str) -> List[Dict]:
    out = []
    page = 1
    while True:
        url = f"{API_BASE}get-chat?page={page}&limit={PAGE_LIMIT}&group_id={group_id}"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        j = r.json()
        data = j.get("data", {})
        out.extend(data.get("data", []))
        nxt = data.get("pagination", {}).get("nextPage")
        if not nxt:
            break
        page = nxt
    return out

def load_seen() -> Set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text()))
        except Exception:
            return set()
    return set()

def save_seen(seen: Set[str]):
    SEEN_FILE.write_text(json.dumps(list(seen), ensure_ascii=False))

def main():
    radio = Si4713Controller(freq_mhz=FM_FREQ, tx_power=FM_PWR)
    seen = load_seen()
    print(f"[FM] tuned to {FM_FREQ:.1f} MHz @ power {FM_PWR} dBuV")
    print(f"[Polling] every {POLL_INTERVAL}s")
    try:
        while True:
            groups = get_all_groups()
            for g in groups:
                gid = g.get("_id")
                gname = g.get("name", "Unknown")
                if not gid:
                    continue
                msgs = get_messages(gid)
                for m in reversed(msgs):
                    mid = m.get("_id")
                    if not mid or mid in seen:
                        continue
                    text = m.get("message", "")
                    user = m.get("user", "Unknown")
                    if not text.strip():
                        seen.add(mid)
                        continue
                    spoken = f"Group {gname}. {user} says: {text}"
                    wav_path = DATA_DIR / f"{mid}.wav"
                    try:
                        espeak_to_wav(spoken, wav_path)
                        play_wav(wav_path)
                        seen.add(mid)
                        save_seen(seen)
                        print(f"[TX] {gname} / {user} / {mid}")
                    except subprocess.CalledProcessError as e:
                        print(f"[ERR] audio pipeline failed: {e}")
            time.sleep(POLL_INTERVAL)
    finally:
        radio.shutdown()

if __name__ == "__main__":
    main()
