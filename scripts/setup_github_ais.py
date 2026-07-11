#!/usr/bin/env python3
"""Create AIS-style labels and starter issues for the smarthome repository.

Requires a GitHub token in GITHUB_TOKEN or GH_TOKEN. The script never prints the
token and only creates labels/issues in the configured repository.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import Request, urlopen

OWNER = os.environ.get("GITHUB_OWNER", "SaJaToGu")
REPO = os.environ.get("GITHUB_REPO", "smarthome")
BASE = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

LABELS: dict[str, dict[str, str]] = {
    "theme/smart-home": {"color": "006b75", "description": "Smart-home control plane and household automation"},
    "theme/home-automation": {"color": "006b75", "description": "Automation logic and schedules"},
    "theme/security": {"color": "d93f0b", "description": "Security, secrets, and access control"},
    "area/jalousien": {"color": "1d76db", "description": "Shutters, blinds, Shelly covers"},
    "area/node-red": {"color": "1d76db", "description": "Node-RED flows, webhooks, dashboard"},
    "area/mqtt": {"color": "1d76db", "description": "Mosquitto, MQTT topics, Shelly MQTT"},
    "area/solar": {"color": "1d76db", "description": "Solar/SENEC data as sensor input"},
    "area/siri": {"color": "1d76db", "description": "iPhone, Siri, Shortcuts, HomeKit"},
    "area/monitoring": {"color": "1d76db", "description": "InfluxDB, Grafana, Uptime Kuma"},
    "kind/feature": {"color": "0e8a16", "description": "New functionality"},
    "kind/docs": {"color": "0075ca", "description": "Documentation"},
    "kind/test": {"color": "c5def5", "description": "Testing and validation"},
    "kind/automation": {"color": "5319e7", "description": "Automation scripts and flows"},
    "state/backlog": {"color": "ededed", "description": "Backlog, not ready yet"},
    "state/ready": {"color": "c2e0c6", "description": "Ready for implementation"},
    "state/blocked": {"color": "d93f0b", "description": "Blocked"},
    "state/review": {"color": "fbca04", "description": "Needs review"},
    "priority/2-high": {"color": "d73a4a", "description": "High priority"},
    "priority/3-medium": {"color": "fbca04", "description": "Medium priority"},
    "priority/4-low": {"color": "0e8a16", "description": "Low priority"},
    "agent/planner": {"color": "5319e7", "description": "AIS planning/backlog shaping"},
    "agent/solver": {"color": "5319e7", "description": "AIS implementation agent"},
    "agent/reviewer": {"color": "5319e7", "description": "AIS review/quality agent"},
}

@dataclass(frozen=True)
class Issue:
    title: str
    labels: list[str]
    body: str

ISSUES = [
    Issue(
        "Solarbasierte Ost-/West-Beschattung für Jalousien bauen",
        ["theme/smart-home", "theme/home-automation", "area/jalousien", "area/node-red", "area/mqtt", "area/solar", "kind/feature", "kind/automation", "state/ready", "priority/2-high", "agent/solver"],
        """## Ziel\n\nDie Solaranlage/SENEC soll als Sonnendetektor für die Jalousie-Beschattung genutzt werden.\n\n## Anforderungen\n\n- Ostseite morgens bei starker Einstrahlung auf 50 %: Küche2, GästeBad, Badezimmer, Arbeitszimmer2.\n- Ab ca. 13:00 Uhr Westseite bei starker Einstrahlung auf 50 %: Schlafzimmer1, Schlafzimmer2, Wohnzimmer1, Wohnzimmer2.\n- Beim Wechsel auf Westseite die Ostseite wieder öffnen.\n- Zufällige Verzögerungen je Rollo, damit es nicht nach Automatisierung aussieht.\n- Hysterese gegen Wolken/kurze PV-Einbrüche.\n\n## Sicherheit\n\nKeine produktive Rollo-Bewegung ohne vorherigen Einzeltest und explizite Freigabe. Keine Secrets in GitHub.\n\n## Referenzen\n\n- `docs/jalousien-shelly.md`\n- `docs/solar-beschattung-konzept.md`\n""",
    ),
    Issue(
        "Manuelle Rollo-Gruppensteuerung in Node-RED erstellen",
        ["theme/smart-home", "area/jalousien", "area/node-red", "area/mqtt", "kind/feature", "state/ready", "priority/2-high", "agent/solver"],
        """## Ziel\n\nManuelle Rollo-Steuerung für Einzelrollos und Gruppen in Node-RED.\n\n## Anforderungen\n\n- Einzelbefehle: hoch, runter, stop, 50 %.\n- Gruppen: Ostseite, Westseite, Räume, alle Rollos.\n- Erst Debug/Test-Modus, danach echte MQTT-Ausgänge.\n- Gen1-Shelly-Topics und Gen2/Gen4-MQTT-RPC sauber trennen.\n\n## Sicherheit\n\nJede Jalousie einzeln testen, bevor Gruppensteuerung aktiviert wird.\n""",
    ),
    Issue(
        "Siri/iPhone-Steuerung per Kurzbefehle planen und umsetzen",
        ["theme/smart-home", "area/siri", "area/node-red", "kind/feature", "kind/automation", "state/backlog", "priority/3-medium", "agent/planner", "agent/solver"],
        """## Ziel\n\nRollos zusätzlich per iPhone/Siri steuern.\n\n## Vorschlag\n\n- Apple Kurzbefehle rufen lokale Node-RED-Webhooks auf.\n- Beispiele: Wohnzimmer Rollos hoch/runter, alle stoppen, Sonnenschutz Ost/West.\n- Kein öffentlicher Node-RED-Zugriff; Heimnetz/VPN bevorzugen.\n- Später Homebridge/HomeKit prüfen.\n\n## Override\n\nSiri-Kommandos sollen später temporär die Automatik übersteuern können.\n\n## Referenz\n\n- `docs/siri-rollo-steuerung.md`\n""",
    ),
    Issue(
        "Node-RED und Smart-Home-Zugriff absichern",
        ["theme/security", "area/node-red", "area/mqtt", "kind/feature", "state/backlog", "priority/3-medium", "agent/planner"],
        """## Ziel\n\nZugriffe auf Node-RED, MQTT und spätere Webhooks sicher halten.\n\n## Aufgaben\n\n- Node-RED AdminAuth dokumentieren und prüfen.\n- MQTT-LAN-Zugriff bewerten; aktuell anonymous im LAN.\n- Siri/Webhook-Endpunkte mit Token/Pfadschutz versehen.\n- Keine Secrets in GitHub, Issues oder Logs.\n""",
    ),
]


def request(method: str, path: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except HTTPError as exc:
        if exc.code == 404:
            return None
        body = exc.read().decode(errors="replace")
        raise SystemExit(f"GitHub API error {exc.code} for {method} {path}: {body}") from exc


def ensure_label(name: str, info: dict[str, str]) -> None:
    escaped = name.replace("/", "%2F")
    existing = request("GET", f"/repos/{OWNER}/{REPO}/labels/{escaped}")
    if existing:
        return
    request("POST", f"/repos/{OWNER}/{REPO}/labels", {"name": name, **info})
    print(f"created label {name}")


def issue_exists(title: str) -> bool:
    items = request("GET", f"/repos/{OWNER}/{REPO}/issues?state=all&per_page=100") or []
    return any("pull_request" not in item and item.get("title") == title for item in items)


def create_issue(issue: Issue) -> None:
    if issue_exists(issue.title):
        print(f"exists issue {issue.title}")
        return
    created = request("POST", f"/repos/{OWNER}/{REPO}/issues", {"title": issue.title, "body": issue.body, "labels": issue.labels})
    print(f"created issue #{created['number']} {issue.title}")


def main() -> int:
    if not TOKEN:
        print("Set GITHUB_TOKEN or GH_TOKEN first", file=sys.stderr)
        return 2
    if request("GET", f"/repos/{OWNER}/{REPO}") is None:
        print(f"Repository {OWNER}/{REPO} not found or token has no access", file=sys.stderr)
        return 3
    for name, info in LABELS.items():
        ensure_label(name, info)
    for issue in ISSUES:
        create_issue(issue)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
