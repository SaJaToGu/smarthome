# AIS-/GitHub-Workflow für das Smart-Home-Repo

Dieses Repo soll GitHub-Issues so strukturieren, dass der AI Issue Solver (AIS) Aufgaben gut erkennen, priorisieren und routen kann.

## Branches

- `main`: stabiler Stand / dokumentierter Betriebszustand.
- `dev`: laufende Entwicklung für neue Smart-Home-Flows, Tests und Dokumentation.
- Feature-Branches nach AIS-Konvention: `ai/fix-issue-N` oder beschreibend `feature/<thema>`.

## Label-Taxonomie

Wir verwenden die AIS-Dimensionen `theme/*`, `area/*`, `kind/*`, `state/*`, `priority/*` und `agent/*`.

### Projektlabels

| Label | Zweck |
|---|---|
| `theme/smart-home` | allgemeine Smart-Home-Zentrale |
| `theme/home-automation` | Automationslogik und Abläufe |
| `theme/security` | Absicherung, Secrets, Zugriffsschutz |
| `area/jalousien` | Rollos/Jalousien/Shelly-Cover |
| `area/node-red` | Node-RED-Flows und Webhooks |
| `area/mqtt` | Mosquitto, MQTT-Topics, Shelly-MQTT |
| `area/solar` | Solaranlage/SENEC als Sensorquelle |
| `area/siri` | iPhone/Siri/Kurzbefehle/HomeKit |
| `area/monitoring` | InfluxDB, Grafana, Uptime Kuma |
| `kind/feature` | neue Funktionalität |
| `kind/docs` | Dokumentation |
| `kind/test` | Tests/Verifikation |
| `kind/automation` | Automationslogik |
| `state/backlog` | Idee, noch nicht bereit |
| `state/ready` | bereit zur Umsetzung |
| `state/blocked` | blockiert, z. B. durch fehlende Freigabe/Secrets |
| `state/review` | in Prüfung |
| `priority/2-high` | wichtig für baldige Umsetzung |
| `priority/3-medium` | normal wichtig |
| `priority/4-low` | später |
| `agent/planner` | Planung/Backlog-Aufbereitung |
| `agent/solver` | Implementierung durch AIS/Agent |
| `agent/reviewer` | Review/Qualitätssicherung |

## Start-Issues

Nach dem Push sollen diese Issues angelegt werden:

### 1. Solarbasierte Ost-/West-Beschattung für Jalousien bauen

Labels: `theme/smart-home`, `theme/home-automation`, `area/jalousien`, `area/node-red`, `area/mqtt`, `area/solar`, `kind/feature`, `kind/automation`, `state/ready`, `priority/2-high`, `agent/solver`

Inhalt:

- SENEC/Solaranlage read-only als Sonnendetektor verwenden.
- Ostseite morgens bei starker Einstrahlung auf 50 %:
  - Küche2
  - GästeBad
  - Badezimmer
  - Arbeitszimmer2
- Ab ca. 13:00 Uhr Westseite beschatten:
  - Schlafzimmer1
  - Schlafzimmer2
  - Wohnzimmer1
  - Wohnzimmer2
- Ostseite dann wieder öffnen.
- Zufällige Verzögerungen verwenden, damit es nicht nach Automatisierung aussieht.
- Hysterese gegen Wolken einbauen.
- Keine Rollo-Bewegung ohne vorherige Einzeltests.

### 2. Manuelle Rollo-Gruppensteuerung in Node-RED erstellen

Labels: `theme/smart-home`, `area/jalousien`, `area/node-red`, `area/mqtt`, `kind/feature`, `state/ready`, `priority/2-high`, `agent/solver`

Inhalt:

- Einzeln und gruppiert: hoch/runter/stop/50 %.
- Ostgruppe und Westgruppe.
- Erst Debug/Test, dann echte MQTT-Ausgänge.
- Gen1-Shelly-Topics und Gen2/Gen4-MQTT-RPC sauber trennen.

### 3. Siri/iPhone-Steuerung per Kurzbefehle planen und umsetzen

Labels: `theme/smart-home`, `area/siri`, `area/node-red`, `kind/feature`, `kind/automation`, `state/backlog`, `priority/3-medium`, `agent/planner`, `agent/solver`

Inhalt:

- Lokale Node-RED-Webhooks für Apple Kurzbefehle.
- Beispiele: Wohnzimmer Rollos hoch/runter, alle stoppen, Sonnenschutz Ost/West.
- Kein öffentlicher Node-RED-Zugriff; Heimnetz/VPN bevorzugen.
- Später Homebridge/HomeKit prüfen.
- Siri-Kommandos sollen temporären Override der Automatik setzen können.

### 4. Node-RED und Smart-Home-Zugriff absichern

Labels: `theme/security`, `area/node-red`, `area/mqtt`, `kind/feature`, `state/backlog`, `priority/3-medium`, `agent/planner`

Inhalt:

- Node-RED-AdminAuth ist eingerichtet; weiter dokumentieren und prüfen.
- MQTT ist aktuell im LAN anonymous erreichbar; später Sicherheitsmodell prüfen.
- Webhooks für Siri mit Token/Pfadschutz versehen.
- Keine Secrets ins Git.

## AIS-Hinweise

- Issues sollten klare Akzeptanzkriterien enthalten.
- Ein AIS-Solver soll bevorzugt auf `dev` arbeiten und PRs gegen `dev` öffnen.
- Vor produktiver Rollo-Automation immer reale MQTT-/Gerätetests dokumentieren.
- Secrets, Passwörter und Tokens niemals in Issues, Logs oder Commits schreiben.
