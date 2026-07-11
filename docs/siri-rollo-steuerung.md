# Siri-/iPhone-Steuerung für Jalousien

## Ziel

Die Rollos sollen zusätzlich zur Zeit-/Solarautomatik per iPhone und Siri steuerbar sein, z. B.:

- „Hey Siri, Wohnzimmer Rollos hoch“
- „Hey Siri, Schlafzimmer Rollos runter“
- „Hey Siri, alle Rollos stoppen“
- „Hey Siri, Sonnenschutz Westseite aktivieren“

Die Sprachsteuerung soll die bestehende Architektur ergänzen, nicht ersetzen:

```text
iPhone / Siri
  → Apple Kurzbefehle oder HomeKit
  → Node-RED
  → MQTT / Shelly
  → Jalousie
```

## Optionen

### Option A — Apple Kurzbefehle + Node-RED Webhooks

Das ist der einfachste und schnellste Weg.

Ablauf:

1. Node-RED stellt lokale Webhook-URLs bereit, z. B.:
   - `/rollo/wohnzimmer/open`
   - `/rollo/wohnzimmer/close`
   - `/rollo/wohnzimmer/stop`
   - `/rollo/west/50`
2. Auf jedem iPhone wird ein Apple-Kurzbefehl angelegt.
3. Siri startet diesen Kurzbefehl per Sprachbefehl.
4. Der Kurzbefehl ruft die Node-RED-URL im Heimnetz auf.
5. Node-RED sendet das passende MQTT-Kommando an die Shellys.

Vorteile:

- kein Home Assistant nötig;
- sehr schnell umzusetzen;
- Sprachbefehle frei formulierbar;
- passt gut zur bestehenden Node-RED/MQTT-Architektur.

Nachteile:

- funktioniert zunächst nur zuverlässig im Heimnetz oder per VPN;
- pro iPhone müssen Kurzbefehle angelegt/geteilt werden;
- nicht so elegant wie echte HomeKit-Geräte in der Apple-Home-App.

Empfehlung: **als erste Stufe verwenden**, weil es wenig Infrastruktur braucht und gut testbar ist.

### Option B — Homebridge / HomeKit

Homebridge kann MQTT-/Shelly-Geräte als HomeKit-Geräte bereitstellen. Dann erscheinen Rollos in der Apple Home App und Siri kann sie nativ steuern.

Ablauf:

```text
Shelly/MQTT ↔ Homebridge ↔ Apple HomeKit ↔ Siri
```

Vorteile:

- Rollos erscheinen als echte Geräte in Apple Home;
- Siri versteht natürlichere Befehle;
- auch Szenen und Räume in Apple Home möglich;
- schöner für tägliche Bedienung.

Nachteile:

- zusätzlicher Dienst im Docker-Stack;
- HomeKit-Bridge muss sauber gepflegt werden;
- MQTT-/Shelly-Topic-Mapping muss exakt stimmen;
- Gen1 und Gen2/Gen4 Shellys unterscheiden sich bei MQTT-Kommandos.

Empfehlung: **zweite Stufe**, wenn die Node-RED-Logik stabil ist.

### Option C — Home Assistant mit HomeKit-Bridge

Home Assistant könnte Shellys erkennen und per HomeKit-Bridge an Apple Home weiterreichen.

Vorteile:

- sehr gute HomeKit-/Siri-Integration;
- viele Integrationen für Gardena, Tesla, Wärmepumpe usw.;
- komfortable UI.

Nachteile:

- größerer Systemumfang;
- wir wollten bewusst schlank mit Node-RED/MQTT starten;
- Automationslogik würde teilweise zwischen Node-RED und Home Assistant aufgeteilt.

Empfehlung: **später prüfen**, wenn weitere Integrationen den Mehrwert rechtfertigen.

## Empfohlener Umsetzungsweg

### Stufe 1 — Sichere lokale Sprachbefehle über Kurzbefehle

Zuerst nur wenige Webhooks in Node-RED:

| Sprachbefehl | Node-RED-Aktion |
|---|---|
| „Wohnzimmer Rollos hoch“ | Wohnzimmer1 + Wohnzimmer2 öffnen |
| „Wohnzimmer Rollos runter“ | Wohnzimmer1 + Wohnzimmer2 schließen oder auf Zielposition fahren |
| „Schlafzimmer Rollos hoch“ | Schlafzimmer1 + Schlafzimmer2 öffnen |
| „Schlafzimmer Rollos runter“ | Schlafzimmer1 + Schlafzimmer2 schließen oder auf Zielposition fahren |
| „Alle Rollos hoch“ | alle definierten Rollos öffnen |
| „Alle Rollos stoppen“ | alle laufenden Rollos stoppen |
| „Sonnenschutz Ostseite“ | Ostgruppe auf 50 % |
| „Sonnenschutz Westseite“ | Westgruppe auf 50 % |

Sicherheitsregeln:

- Webhooks nur im Heimnetz erreichbar machen.
- Keine offenen Internet-Ports für Node-RED.
- Optional einen einfachen geheimen Pfad oder Token verwenden, z. B. `/rollo/<token>/wohnzimmer/open`.
- Zuerst nur Debug-Ausgabe, dann einzelne Rollos, dann Gruppen.

### Stufe 2 — Apple Home/HomeKit schöner machen

Wenn Stufe 1 zuverlässig läuft:

- Homebridge als Docker-Service ergänzen;
- Rollos als HomeKit-Geräte abbilden;
- Räume und Szenen in Apple Home definieren;
- Siri-Befehle natürlicher machen.

### Stufe 3 — Externe Bedienung

Falls Sprachsteuerung auch unterwegs funktionieren soll:

- bevorzugt VPN ins Heimnetz;
- alternativ Apple Home Hub/HomeKit, wenn Homebridge stabil läuft;
- keine direkte öffentliche Node-RED-Freigabe.

## Beziehung zur Solar-Beschattung

Siri-Kommandos sollen die Automatik nicht unkontrolliert bekämpfen. Deshalb sollte später eine Override-Logik eingeführt werden:

- manuelles Siri-Kommando setzt einen temporären Override;
- Automatik respektiert den Override z. B. 1–3 Stunden;
- „Automatik wieder aktivieren“ kann als eigener Siri-Befehl angelegt werden.

Beispiele:

| Sprachbefehl | Wirkung |
|---|---|
| „Sonnenschutz Ostseite aktivieren“ | Ostrollos auf 50 %, Override aktiv |
| „Sonnenschutz Westseite aktivieren“ | Westrollos auf 50 %, Override aktiv |
| „Rollo Automatik wieder aktivieren“ | Override löschen, Solar-/Zeitlogik übernimmt wieder |

## Empfehlung

Für den Start: **Apple Kurzbefehle → Node-RED Webhooks → MQTT/Shelly**.

Das ist schlank, passt zur aktuellen Architektur und kann ohne Home Assistant umgesetzt werden. Wenn die Rollo-Logik stabil ist, kann Homebridge später für eine schönere HomeKit-/Siri-Integration ergänzt werden.
