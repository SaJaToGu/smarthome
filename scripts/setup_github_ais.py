#!/usr/bin/env python3
"""Create AIS-style labels and starter issues on GitHub for the smarthome repo.

Usage: python3 setup_github_ais.py
Requires: GITHUB_TOKEN or GH_TOKEN environment variable, or a GitHub CLI token
on the iMac2 accessed via SSH.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

TOKEN_ENV_VARS = ["GITHUB_TOKEN", "GH_TOKEN"]


def get_token_from_imac2() -> str | None:
    import subprocess

    result = subprocess.run(
        [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
            "-i", os.path.expanduser("~/.ssh/metis_ed25519"),
            "Guido@192.168.178.43",
            "python3", "-c",
            "import re,os;t=open(os.path.expanduser('~/.config/gh/hosts.yml')).read();"
            "print(re.search(r'oauth_token:\\s*(\\S+)',t).group(1))",
        ],
        text=True,
        capture_output=True,
        timeout=15,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def get_token() -> str:
    for var in TOKEN_ENV_VARS:
        token = os.environ.get(var, "").strip()
        if token:
            return token
    token = get_token_from_imac2()
    if token:
        return token
    print(
        "FEHLER: Kein GitHub Token gefunden. "
        "Setze GITHUB_TOKEN oder nutze iMac2-Zugang.", file=sys.stderr
    )
    sys.exit(2)


API = "https://api.github.com"
REPO = "SaJaToGu/smarthome"


def api(method: str, path: str, data: dict | None = None) -> dict:
    token = get_token()
    url = f"{API}{path}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "smarthome-setup-script",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()[:400]
        print(f"HTTP {e.code} für {method} {path}: {e.reason}", file=sys.stderr)
        print(body_text, file=sys.stderr)
        sys.exit(1)


def label_exists(name: str) -> bool:
    try:
        api("GET", f"/repos/{REPO}/labels/{name.replace('/', '%2F')}")
        return True
    except SystemExit:
        return False


def create_label(name: str, color: str, description: str) -> None:
    encoded_name = name.replace("/", "%2F")
    if label_exists(name):
        print(f"  Label existiert bereits: {name}")
        return
    api(
        "POST",
        f"/repos/{REPO}/labels",
        {"name": name, "color": color, "description": description},
    )
    print(f"  Label erstellt: {name}")


def create_issue(title: str, body: str, labels: list[str]) -> None:
    result = api(
        "POST",
        f"/repos/{REPO}/issues",
        {"title": title, "body": body, "labels": labels},
    )
    print(f"  Issue erstellt: #{result.get('number')} — {title}")


def main() -> None:
    print("=" * 60)
    print("GitHub AIS-Setup für SaJaToGu/smarthome")
    print("=" * 60)

    # --- Labels ---
    print("\nLabels werden erstellt...")
    labels = [
        # theme
        ("theme/smart-home",     "4c8f4f", "Betrifft das gesamte Smart-Home-System"),
        ("theme/home-automation","3a8f8f", "Home-Automation, MQTT, Node-RED"),
        ("theme/infrastructure",  "7a7a7a", "Infrastruktur, Docker, Raspberry-Pi"),
        ("theme/security",        "c0392b", "Sicherheit, Absicherung, Credentials"),
        # area
        ("area/jalousien",       "f39c12", "Jalousien-Rolladen-Steuerung"),
        ("area/node-red",         "2980b9", "Node-RED Flows und Automation"),
        ("area/mqtt",             "27ae60", "MQTT-Broker und Topics"),
        ("area/solar",            "f1c40f", "Solar/SENEC und Beschattung"),
        ("area/siri",             "8e44ad", "Siri/iPhone-Steuerung"),
        ("area/health",           "e74c3c", "System-Gesundheit, Monitoring"),
        # kind
        ("kind/feature",          "2ecc71", "Neue Funktionalität"),
        ("kind/automation",       "3498db", "Automatisierungslogik"),
        ("kind/bug",              "e74c3c", "Fehler oder Problem"),
        ("kind/docs",             "95a5a6", "Dokumentation"),
        ("kind/refactor",         "7f8c8d", "Code umbauen"),
        # state
        ("state/backlog",          "bdc3c7", "Backlog — noch nicht geplant"),
        ("state/ready",           "27ae60", "Bereit zur Umsetzung"),
        ("state/in-progress",      "3498db", "Wird gerade bearbeitet"),
        ("state/blocked",          "e74c3c", "Blockiert"),
        ("state/done",             "7f8c8d", "Erledigt"),
        # priority
        ("priority/1-critical",    "c0392b", "Kritisch — sofort"),
        ("priority/2-high",       "e67e22", "Hohe Priorität"),
        ("priority/3-medium",     "f1c40f", "Mittlere Priorität"),
        ("priority/4-low",        "bdc3c7", "Niedrige Priorität"),
        # agent
        ("agent/planner",          "9b59b6", "Planung/Routing durch AIS"),
        ("agent/solver",           "1abc9c", "Durch AIS lösbar"),
        ("agent/human",            "95a5a6", "Mensch muss ran"),
    ]
    for name, color, desc in labels:
        create_label(name, color, desc)

    # --- Starter Issues ---
    print("\nStarter-Issues werden erstellt...")
    starter_issues = [
        (
            "Solarbasierte Ost-/West-Beschattung für Jalousien bauen",
            """## Beschreibung

Die Jalousien sollen basierend auf der PV-Leistung der SENEC-Solaranlage (192.168.178.121) automatisch gesteuert werden.

### Anforderungen

- SENEC-Solarleistung read-only abfragen (bereits vorbereitet)
- PV-Leistung über 2500 W → Beschattung aktiv
- Ostseite (Küche2, GästeBad, Badezimmer, Arbeitszimmer2) nur 07:00–13:00 Uhr
- Westseite (Schlafzimmer1/2, Wohnzimmer1/2) ab 13:00 Uhr
- Zufälliger Versatz 30 s–8 min für natürliches Verhalten
- Hysterese: unter 1200 W lösen

### Status

Bereits vorbereitet als deaktivierter Node-RED-Flow: `ENTWURF Solar-Beschattung Jalousien`

Nächste Schritte:
1. Debug-Plan manuell prüfen
2. Einzelne Rollo-Positionsbefehle testen
3. MQTT-Ausgänge mit Zufallsversatz anschließen
4. Flow aktivieren
""",
            ["theme/smart-home", "area/solar", "area/jalousien", "kind/automation", "state/ready", "priority/2-high", "agent/solver"],
        ),
        (
            "Manuelle Rollo-Gruppensteuerung in Node-RED erstellen",
            """## Beschreibung

Vor der Solar-Automatisierung müssen die Jalousien einzeln und gruppiert steuerbar sein.

### Anforderungen

- Jede Jalousie einzeln: Küche2, GästeBad, Badezimmer, Arbeitszimmer2, Schlafzimmer1, Schlafzimmer2, Wohnzimmer1, Wohnzimmer2
- Gruppen: Ostseite (Küche2, GästeBad, Badezimmer, Arbeitszimmer2), Westseite (Schlafzimmer1, Schlafzimmer2, Wohnzimmer1, Wohnzimmer2)
- Befehle: Position 0–100 %, Stop, Hoch, Runter
- Nur MQTT-Topics, keine direkte HTTP-Kommandos

### Status

Bereits vorbereitet: Basis-Flow mit MQTT-Verbindung

Nächste Schritte:
1. Einzelne Shelly-Positionsbefehle je Rollo testen
2.Gruppensteuerung als separate Node-RED-Subflows bauen
3. Notfall-Override: Alle stoppen / Alle hoch
""",
            ["theme/smart-home", "area/jalousien", "area/node-red", "kind/feature", "state/ready", "priority/2-high", "agent/solver"],
        ),
        (
            "Siri/iPhone-Steuerung für Rollos einrichten",
            """## Beschreibung

Per iPhone-Sprachbefehl sollen die Rollos steuerbar sein.

### Anforderungen

- Siri-Kurzbefehle auf dem iPhone
- Node-RED Webhook als Empfänger (HTTP POST)
- Befehle: "Wohnzimmer Rollos hoch", "Schlafzimmer Rollos runter", "Alle Rollos stoppen"
- Manueller Eingriff soll temporäre Override setzen, damit Automatik nicht sofort zurücksetzt
- Später optional: Homebridge/HomeKit für native Apple-Home-App-Unterstützung

### Status

Konzept bereits dokumentiert in `docs/siri-rollo-steuerung.md`

Nächste Schritte:
1. Node-RED HTTP-Endpunkt für Webhook-Befehle anlegen
2. Siri-Kurzbefehle auf iPhone einrichten und testen
3. Override-Logik ergänzen
""",
            ["theme/smart-home", "area/siri", "area/jalousien", "kind/feature", "state/backlog", "priority/3-medium", "agent/human"],
        ),
        (
            "Node-RED-Access und Smart-Home-Auth absichern",
            """## Beschreibung

Node-RED und das Smart-Home-System müssen sicher betrieben werden.

### Anforderungen

- [x] Node-RED adminAuth eingerichtet (admin-Passwort in `.secrets/nodered-admin.txt`)
- [ ] HTTPS/TLS für Node-RED UI (oder Zugriff nur über LAN/VPN)
- [ ] MQTT-Client auf Node-RED: saubere Auth, kein anonymous
- [ ] Mosquitto: ACLs prüfen, kein anonymer Zugriff von außen
- [ ] SSH-Hardening auf Raspberry Pi
- [ ] Regelmäßige Log-Überprüfung auf Anomalien
- [ ] Backup-Strategie für Flows, InfluxDB, Konfiguration

### Status

adminAuth ist eingerichtet. Mosquitto läuft systemweit.

Nächste Schritte:
1. MQTT-Zugang auf Pi-local beschränken
2. Backup-Konfiguration dokumentieren
3. Optional: VPN-Zugang für Fernzugriff
""",
            ["theme/security", "area/node-red", "area/mqtt", "kind/feature", "state/ready", "priority/1-critical", "agent/solver"],
        ),
        (
            "SMART/SSD-Monitoring für Raspberry-Pi-SSD einrichten",
            """## Beschreibung

Die 32-GB-SSD soll per SMART überwacht werden, um Ausfälle frühzeitig zu erkennen.

### Anforderungen

- `smartmontools` installieren
- SMART-Daten für `/dev/sda` regelmäßig auswerten
- Kritische Werte: Reallocated_Sector_Ct, Current_Pending_Sector, Offline_Uncorrectable
- Bei Auffälligkeiten: Alert per Hermes
- Alternativ: S.M.A.R.T. über USB-SATA-Bridge prüfen (Bridge-Typ ermitteln)

### Status

Monitoring-Script `rpi_health_watch.py` ist vorbereitet, SMART-Prüfung ist noch eingeschränkt.

Nächste Schritte:
1. `smartmontools` installieren: `sudo apt-get install -y smartmontools`
2. SMART-Test: `sudo smartctl -a /dev/sda` und `sudo smartctl -d sat -a /dev/sda`
3. Script um SMART-Check erweitern wenn verfügbar
4. Regelmäßige Prüfung in Cron einbauen
""",
            ["theme/infrastructure", "area/health", "kind/feature", "state/ready", "priority/2-high", "agent/solver"],
        ),
    ]

    for title, body, labels in starter_issues:
        create_issue(title, body, labels)

    print("\n" + "=" * 60)
    print("Fertig! Repo: https://github.com/SaJaToGu/smarthome")
    print("=" * 60)


if __name__ == "__main__":
    main()
