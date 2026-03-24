#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.parse
import urllib.request


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("\"'")  # allow quoted values
            os.environ.setdefault(key, val)

load_env()

COURSE_URL = "https://spo.isdc.co.kr/courseListAjax.ajax"

# Filters for the target class. Adjust if the program name changes.
TARGET_PGM_NM = os.environ.get("TARGET_PGM_NM", "수영_초급반_월,화,목,금_07:00_2개월차")
TARGET_ITEM_NM = os.environ.get("TARGET_ITEM_NM", "초급반")
TARGET_WEEK = os.environ.get("TARGET_WEEK", "월화목금")
TARGET_START_T = os.environ.get("TARGET_START_T", "0700")
TARGET_END_T = os.environ.get("TARGET_END_T", "0750")

PARAMS = {
    "up_id": os.environ.get("UP_ID", "02"),       # Seongnam Sports Complex
    "bas_cd": os.environ.get("BAS_CD", "01"),     # Swimming
    "item_cd": os.environ.get("ITEM_CD", "00"),   # All
    "pgm_nm": "",
    "week_nm": "",
    "target_cd": os.environ.get("TARGET_CD", "99"),  # All
    "page": 0,
    "perPageNum": 100,
    "ju_dc": "",
}

POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "60"))


def fetch_courses():
    data = urllib.parse.urlencode(PARAMS).encode()
    req = urllib.request.Request(COURSE_URL, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw).get("data", [])


def is_target_row(row):
    if TARGET_PGM_NM:
        return row.get("pgm_nm") == TARGET_PGM_NM
    return (
        row.get("item_nm") == TARGET_ITEM_NM
        and row.get("week_nm", "") == TARGET_WEEK
        and row.get("start_t") == TARGET_START_T
        and row.get("end_t") == TARGET_END_T
    )


def seat_available(row):
    try:
        now_cnt = int(row.get("group_regi_inwon", "0"))
        cap_cnt = int(row.get("group_rgl_qty", "0"))
    except ValueError:
        return False, "0/0"
    return now_cnt < cap_cnt, f"{now_cnt}/{cap_cnt}"


def send_telegram(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        _ = resp.read()
    return True


def main():
    print("Starting swim seat watcher...", flush=True)
    print(f"Target program: {TARGET_PGM_NM or 'auto-match'}", flush=True)
    was_full = True

    while True:
        try:
            rows = fetch_courses()
            target = next((r for r in rows if is_target_row(r)), None)
            if not target:
                print("Target class not found in response.")
            else:
                available, ratio = seat_available(target)
                print(f"Status: {ratio}")
                if was_full and available:
                    msg = (
                        "Seat opened!\n"
                        f"{target.get('up_nm')} / {target.get('bas_nm')}\n"
                        f"{target.get('pgm_nm')}\n"
                        f"{ratio}"
                    )
                    send_telegram(msg)
                was_full = not available
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
