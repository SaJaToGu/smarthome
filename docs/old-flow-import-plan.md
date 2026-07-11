# Importplan alter Node-RED Flow

Quelle: `imports/flows_07-04-2024.json`

Sichere Import-Vorlage: `imports/flows_07-04-2024.DISABLED-SAFE-MIGRATED.json`

## Grundsatz

Den alten Flow **nicht direkt produktiv deployen**. Er enthält aktive Timer und Ausgänge für Jalousien, Außenlicht, Tesla, Backup-Skripte und E-Mail. Ein unkontrollierter Deploy könnte Geräte bewegen oder Aktionen auslösen.

## Was bereits vorbereitet wurde

- Originaldatei im Repo gesichert.
- Analyse erzeugt: `docs/generated/old-flow-analysis.md`.
- Sichere Import-Datei erzeugt:
  - alle Tabs sind deaktiviert;
  - Tab-Namen sind mit `ALT` markiert;
  - MQTT-Broker `smarthome`/`localhost` wurde auf `192.168.178.40` umgestellt;
  - MQTT-Client-ID für alten Flow geändert, um Konflikte zu vermeiden.

## Benötigte Node-RED-Pakete vor vollständigem Import

```text
node-red-dashboard
node-red-contrib-bigtimer
node-red-contrib-fritzbox
node-red-contrib-influxdb
node-red-contrib-modbus
node-red-contrib-sun-position
node-red-contrib-tesla
node-red-node-email
```

## Empfohlene Reihenfolge

1. Node-RED Paketliste gezielt installieren.
2. Node-RED neu starten und prüfen.
3. Sichere Import-Datei importieren, aber noch **nicht aktivieren**.
4. Zuerst nur Jalousie-Tabs prüfen:
   - Küche
   - Wohnzimmer
   - Arbeitszimmer
   - Badezimmer Gäste
   - Badezimmer 1.OG
   - Schlafzimmer
   - Jans Zimmer
   - Tills Zimmer
5. Alte Shelly-Topic-IDs gegen aktuelle Geräte abgleichen.
6. Pro Raum jeweils nur manuelle Steuerung testen.
7. Zeit-/Sonnen-Automatiken erst danach einzeln aktivieren.
8. Tesla/PV, FritzBox, InfluxDB, Backup und E-Mail separat migrieren.

## Besonders vorsichtig behandeln

- `Sonne`: enthält zentrale Timer und Link-Ausgänge zu mehreren Räumen.
- `Aussenbeleuchtung Eingangstür`: schaltet Außenlicht per Timer.
- `Solaranlage`: enthält Tesla-API und SENEC-Abfrage.
- `Backup MyPi`: enthält `sudo raspiBackup.sh` und E-Mail-Versand.
- `Fritz!Box who is present`: enthält alte MAC-Adressen zur Anwesenheitserkennung.

## Aktueller Fokus

Für die nächste Phase nur Jalousien übernehmen, nicht den gesamten alten Flow produktiv schalten.
