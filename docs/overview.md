# Übersicht Smart-Home-Zentrale

## Architektur

```text
Hermes / Telegram
      │
      ▼
Raspberry Pi metis-rpi-control / 192.168.178.40
      │
      ├── Mosquitto als Systemdienst :1883
      │       └── Shelly/Jalousien/Außenlicht per MQTT
      │
      ├── Node-RED :1880
      │       └── Automationen, PV-Überschusslogik, Skriptsteuerung
      │
      ├── InfluxDB :8086
      │       └── Messwerte und Langzeitdaten
      │
      ├── Grafana :3000
      │       └── Dashboards
      │
      └── Uptime Kuma :3001
              └── Netzwerk- und Dienstüberwachung
```

## Teilbereiche

- `jalousien-shelly.md` — Shelly/Jalousien/MQTT
- `pv-tesla.md` — PV-Überschussladen Tesla
- `waermepumpe.md` — Wärmepumpe Monitoring
- `gardena.md` — Gardena Bewässerung
- `aussenlicht.md` — Außenlicht
- `netzwerk-monitoring.md` — LAN/WLAN Monitoring und Verbesserung

## Offene Entscheidungen

- Home Assistant erst später hinzufügen, falls Integrationen für Gardena, Tesla oder Wärmepumpe dadurch deutlich einfacher werden.
- Mosquitto vorerst nicht in Docker migrieren, weil die Shellys bereits produktiv verbunden sind.
