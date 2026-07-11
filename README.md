# Smart-Home-Zentrale Raspberry Pi

Dieses Repo enthält die Konfiguration für den Smart-Home-Stack auf dem Raspberry Pi `metis-rpi-control` (`192.168.178.40`).

## Ziele

1. Jalousien über Shelly/MQTT steuern
2. PV-Überschussladen des Teslas vorbereiten
3. Wärmepumpe monitoren
4. Gardena-Bewässerung integrieren, falls möglich
5. Außenlicht steuern
6. LAN/WLAN überwachen und verbessern

## Grundentscheidung

- **Mosquitto/MQTT bleibt vorerst als Systemdienst** auf dem Raspberry Pi laufen.
- Docker wird für ergänzende Dienste genutzt.
- Home Assistant ist vorerst **optional**, nicht Pflicht.
- Node-RED soll zunächst die Automations- und Logikzentrale werden.
- Hermes dient als Steuer-, Diagnose- und Administrationsoberfläche über Telegram.

## Aktuelle Basisdienste

| Dienst | Zweck | Port |
|---|---|---:|
| Mosquitto | MQTT-Broker für Shelly/Jalousien | 1883 |
| Node-RED | Automationen und Steuerlogik | 1880 |
| InfluxDB | Zeitreihendaten | 8086 |
| Grafana | Dashboards | 3000 |
| Uptime Kuma | Netzwerk-/Dienst-Monitoring | 3001 |

## Bedienung

```bash
cd /home/guido/smarthome

# Stack prüfen
docker-compose config

# Dienste starten
docker-compose up -d

# Status anzeigen
docker-compose ps

# Logs ansehen
docker-compose logs -f --tail=100

# Dienste stoppen
docker-compose down
```

## Wichtige Hinweise

- Docker-Gruppenmitgliedschaft für `guido` wurde gesetzt. Falls `docker` ohne `sudo` noch nicht geht, einmal neu einloggen oder den Raspberry Pi neu starten.
- MQTT läuft aktuell außerhalb von Docker als Systemdienst und ist unter `192.168.178.40:1883` erreichbar.
- Node-RED ist passwortgeschützt. Die lokalen Zugangsdaten liegen absichtlich nicht im Git, sondern unter `/home/guido/smarthome/.secrets/`.
- Keine produktiven Automationen ohne vorherige manuelle Prüfung aktivieren.
