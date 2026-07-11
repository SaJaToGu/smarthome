#!/usr/bin/env python3
"""Quiet Raspberry Pi power/SSD watchdog for Hermes cron.

Default mode prints only alerts. Use --status for a human-readable baseline.
State is stored outside Git in /var/tmp so recurring checks do not spam the user.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

STATE_PATH = Path(os.environ.get("SMARTHOME_RPI_HEALTH_STATE", "/var/tmp/smarthome-rpi-health-state.json"))
HOST = os.uname().nodename
JOURNAL_PATTERNS = re.compile(
    r"under.?voltage|thrott|voltage|reset|i/o error|ext4|filesystem|nvme|usb|uas|sda|mmc|"
    r"blk_update|buffer i/o|read-only|corrupt|error",
    re.IGNORECASE,
)
THROTTLE_BITS = {
    0: "Unterspannung aktuell",
    1: "ARM-Frequenz aktuell begrenzt",
    2: "aktuell gedrosselt",
    3: "Soft-Temperaturlimit aktuell aktiv",
    16: "Unterspannung seit Boot aufgetreten",
    17: "ARM-Frequenz seit Boot begrenzt",
    18: "Drosselung seit Boot aufgetreten",
    19: "Soft-Temperaturlimit seit Boot aufgetreten",
}


def run(cmd: list[str], timeout: int = 10) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as exc:  # noqa: BLE001 - watchdog must not crash on one probe
        return 999, f"{type(exc).__name__}: {exc}"


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def get_boot_id() -> str:
    path = Path("/proc/sys/kernel/random/boot_id")
    return path.read_text().strip() if path.exists() else "unknown"


def root_source() -> str:
    rc, out = run(["findmnt", "-no", "SOURCE", "/"])
    return out.splitlines()[0].strip() if rc == 0 and out else "unknown"


def root_block_device() -> str | None:
    source = root_source()
    # /dev/sda2 -> /dev/sda, /dev/nvme0n1p2 -> /dev/nvme0n1
    if source.startswith("/dev/nvme"):
        return re.sub(r"p\d+$", "", source)
    if source.startswith("/dev/sd") or source.startswith("/dev/mmcblk"):
        return re.sub(r"\d+$", "", source).rstrip("p")
    return None


def parse_throttled(raw: str) -> tuple[int | None, list[str]]:
    match = re.search(r"throttled=0x([0-9a-fA-F]+)", raw)
    if not match:
        return None, [f"vcgencmd get_throttled nicht lesbar: {raw}"]
    value = int(match.group(1), 16)
    return value, [text for bit, text in THROTTLE_BITS.items() if value & (1 << bit)]


def power_status(alerts: list[str], status: list[str]) -> dict:
    data: dict[str, object] = {}
    if not shutil.which("vcgencmd"):
        alerts.append("vcgencmd fehlt; Raspberry-Pi-Unterspannungsstatus kann nicht gelesen werden.")
        return data
    rc, raw = run(["vcgencmd", "get_throttled"])
    value, flags = parse_throttled(raw)
    data["throttled_raw"] = raw
    data["throttled_value"] = value
    status.append(f"Power/throttling: {raw or 'unbekannt'}")
    if rc != 0 or value is None:
        alerts.append(f"Powerstatus nicht lesbar: {raw}")
    elif flags:
        alerts.append("Raspberry-Pi-Power/Throttling-Warnung: " + ", ".join(flags) + f" ({raw})")

    rc, temp = run(["vcgencmd", "measure_temp"])
    data["temp_raw"] = temp
    status.append(f"Temperatur: {temp or 'unbekannt'}")
    m = re.search(r"temp=([0-9.]+)'C", temp)
    if m and float(m.group(1)) >= 75:
        alerts.append(f"Raspberry Pi Temperatur hoch: {m.group(1)} °C")
    return data


def filesystem_status(alerts: list[str], status: list[str]) -> None:
    rc, mount = run(["findmnt", "-no", "SOURCE,FSTYPE,OPTIONS", "/"])
    status.append(f"Root-FS: {mount or 'unbekannt'}")
    if " ro," in f" {mount}," or mount.endswith(" ro"):
        alerts.append(f"Root-Dateisystem ist read-only: {mount}")
    rc, df = run(["df", "-P", "/"])
    lines = df.splitlines()
    if len(lines) >= 2:
        parts = lines[1].split()
        if len(parts) >= 5:
            status.append(f"Root-Belegung: {parts[4]} belegt, {parts[3]} KB frei")
            try:
                used = int(parts[4].rstrip("%"))
                if used >= 85:
                    alerts.append(f"Root-Dateisystem fast voll: {parts[4]} belegt")
            except ValueError:
                pass


def smart_status(alerts: list[str], status: list[str], state: dict) -> None:
    dev = root_block_device()
    status.append(f"Root-Blockgerät: {dev or 'unbekannt'}")
    if not dev:
        alerts.append("Root-Blockgerät konnte nicht bestimmt werden; SSD-Monitoring eingeschränkt.")
        return
    if not shutil.which("smartctl"):
        # Alert once; repeated reminders would be noisy.
        if not state.get("smartctl_missing_reported"):
            alerts.append(
                "SMART-Monitoring ist noch eingeschränkt: smartctl/smartmontools ist nicht installiert. "
                "Kernel-/Filesystem-Fehler werden trotzdem überwacht."
            )
            state["smartctl_missing_reported"] = True
        return

    rc, out = run(["sudo", "smartctl", "-H", "-A", dev], timeout=20)
    status.append(f"SMART {dev}: {'ok gelesen' if rc == 0 else 'nicht lesbar'}")
    if rc != 0:
        # Some USB bridges need SAT passthrough.
        rc2, out2 = run(["sudo", "smartctl", "-d", "sat", "-H", "-A", dev], timeout=20)
        if rc2 == 0:
            out = out2
            rc = 0
            status.append(f"SMART {dev}: mit -d sat gelesen")
    if rc != 0:
        alerts.append(f"SMART-Daten für {dev} nicht lesbar: {out.splitlines()[:3]}")
        return
    if re.search(r"SMART overall-health.*FAILED|SMART Health Status:\s*FAILED", out, re.I):
        alerts.append(f"SMART meldet FEHLER für {dev}")
    for attr in ["Reallocated_Sector_Ct", "Current_Pending_Sector", "Offline_Uncorrectable", "UDMA_CRC_Error_Count", "Media_Wearout_Indicator"]:
        m = re.search(rf"\b{attr}\b.*?\s(\d+)\s*$", out, re.M)
        if m and int(m.group(1)) > 0 and attr != "Media_Wearout_Indicator":
            alerts.append(f"SMART auffällig auf {dev}: {attr}={m.group(1)}")


def journal_status(alerts: list[str], status: list[str], state: dict, force_status: bool) -> None:
    since = state.get("last_check_iso") or "24 hours ago"
    rc, out = run(["journalctl", "-k", "--since", since, "--no-pager"], timeout=20)
    matches = [line for line in out.splitlines() if JOURNAL_PATTERNS.search(line)] if rc == 0 else []
    # Ignore the known one-time boot cache message unless status mode wants visibility.
    actionable = [line for line in matches if "Assuming drive cache: write through" not in line]
    status.append(f"Kernel-Warnmuster seit {since}: {len(actionable)} Treffer")
    if actionable:
        alerts.append("Kernel/SSD/USB/Filesystem-Warnungen:\n" + "\n".join(actionable[-12:]))
    elif force_status and matches:
        status.append("Nur unkritische/übliche Kernel-Treffer gesehen: " + " | ".join(matches[-3:]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="always print baseline status")
    args = parser.parse_args()

    state = load_state()
    alerts: list[str] = []
    status: list[str] = []
    boot_id = get_boot_id()
    if state.get("boot_id") and state.get("boot_id") != boot_id:
        alerts.append(f"Raspberry Pi wurde neu gestartet. Neuer boot_id={boot_id}")
    state["boot_id"] = boot_id

    power_status(alerts, status)
    filesystem_status(alerts, status)
    smart_status(alerts, status, state)
    journal_status(alerts, status, state, args.status)

    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    state["last_check_iso"] = now_iso
    save_state(state)

    if alerts:
        print(f"⚠️ RPI/SSD-Monitor {HOST} — {now_iso}")
        print("\n\n".join(alerts))
        if args.status:
            print("\nStatus:\n" + "\n".join(f"- {line}" for line in status))
        # For Hermes no_agent cron, non-empty stdout is the alert. Keep exit 0 so
        # the scheduler sends the message verbatim instead of wrapping it as a
        # broken-watchdog error.
        return 0
    if args.status:
        print(f"✅ RPI/SSD-Monitor {HOST} — {now_iso}")
        print("\n".join(f"- {line}" for line in status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
