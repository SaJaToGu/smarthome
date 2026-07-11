# Jalousien und Shelly

## Status

- MQTT-Broker: `192.168.178.40:1883`
- 13 Jalousien-Shellys sind auf MQTT konfiguriert.
- Gästebad wurde als Shelly `192.168.178.33` identifiziert.

## Ziel

- Alle Jalousien einzeln und gruppiert steuern.
- Zustände über MQTT erfassen.
- Später Automationen für Zeiten, Sonnenstand und manuelle Szenen einrichten.
- Zusätzlich iPhone-/Siri-Steuerung ermöglichen; Konzept siehe `docs/siri-rollo-steuerung.md`.

## Nächste Schritte

1. MQTT-Topics aller Shellys dokumentieren.
2. Geräte sinnvoll benennen.
3. Node-RED Flow für `alle hoch`, `alle runter`, `stop` erstellen.
4. Manuelle Tests pro Raum durchführen.
5. Danach lokale Siri-Kurzbefehle über sichere Node-RED-Webhooks vorbereiten.
