# Analyse alter Node-RED Flow `flows_07-04-2024.json`

## Zusammenfassung

- Knoten insgesamt: **309**
- Tabs: **22**
- MQTT-Ausgänge: **17**
- MQTT-Eingänge: **72**

## Benötigte Node-RED Zusatzpakete

- `node-red-contrib-bigtimer`
- `node-red-contrib-fritzbox`
- `node-red-contrib-influxdb`
- `node-red-contrib-modbus`
- `node-red-contrib-sun-position`
- `node-red-contrib-tesla`
- `node-red-dashboard`
- `node-red-node-email`

## Tabs

- **Sonne** — 10 Nodes, MQTT in/out 0/0, Timer 5
- **Solaranlage ** — 22 Nodes, MQTT in/out 0/0, Timer 0
- **Aussenbeleuchtung Eingangstür** — 7 Nodes, MQTT in/out 1/1, Timer 2
- **Küche** — 15 Nodes, MQTT in/out 5/2, Timer 0
- **Wohnzimmer** — 11 Nodes, MQTT in/out 2/2, Timer 0
- **Arbeitszimmer** — 10 Nodes, MQTT in/out 2/2, Timer 0
- **Badezimmer Gäste** — 6 Nodes, MQTT in/out 1/1, Timer 0
- **Badezimmer 1.OG** — 10 Nodes, MQTT in/out 3/1, Timer 0
- **Schlafzimmer** — 17 Nodes, MQTT in/out 3/3, Timer 0
- **Jans Zimmer** — 18 Nodes, MQTT in/out 5/2, Timer 3
- **Tills Zimmer** — 8 Nodes, MQTT in/out 1/1, Timer 0
- **Fritz!Box who is present** — 16 Nodes, MQTT in/out 4/1, Timer 0
- **Shellys** — 28 Nodes, MQTT in/out 14/0, Timer 0
- **Backup MyPi** — 4 Nodes, MQTT in/out 0/0, Timer 0
- **Garage** — 6 Nodes, MQTT in/out 3/0, Timer 0
- **Speisekammer** — 10 Nodes, MQTT in/out 5/0, Timer 0
- **Keller Hobbyraum** — 12 Nodes, MQTT in/out 6/0, Timer 0
- **Batteriestatus** — 26 Nodes, MQTT in/out 13/0, Timer 0
- **Test mqtt** — 6 Nodes, MQTT in/out 2/1, Timer 0
- **Dachboden** — 2 Nodes, MQTT in/out 1/0, Timer 0
- **Heizungsraum** — 2 Nodes, MQTT in/out 1/0, Timer 0

## Shelly-/Jalousie-Topics aus altem Flow

| Device-ID im Topic | Tabs | Typen | Beispiel-Topics |
|---|---|---|---|
| `+` | Shellys | mqtt in | shellies/+/roller/0/pos |
| `shelly1-E098068CC9EB` | Aussenbeleuchtung Eingangstür | mqtt in, mqtt out | shellies/shelly1-E098068CC9EB/relay/0<br>shellies/shelly1-E098068CC9EB/relay/0/command |
| `shellyswitch25-1097AB` | Schlafzimmer, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-1097AB/roller/0/command<br>shellies/shellyswitch25-1097AB/roller/0/pos<br>shellies/shellyswitch25-1097AB/temperature |
| `shellyswitch25-1097D5` | Badezimmer 1.OG, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-1097D5/roller/0/command<br>shellies/shellyswitch25-1097D5/roller/0/pos<br>shellies/shellyswitch25-1097D5/temperature |
| `shellyswitch25-10986E` | Arbeitszimmer, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-10986E/roller/0/command<br>shellies/shellyswitch25-10986E/roller/0/pos<br>shellies/shellyswitch25-10986E/temperature |
| `shellyswitch25-109899` | Shellys, Tills Zimmer | mqtt in, mqtt out | shellies/shellyswitch25-109899/roller/0/command<br>shellies/shellyswitch25-109899/roller/0/pos<br>shellies/shellyswitch25-109899/temperature |
| `shellyswitch25-1099CC` | Shellys, Wohnzimmer | mqtt in, mqtt out | shellies/shellyswitch25-1099CC/roller/0/command<br>shellies/shellyswitch25-1099CC/roller/0/pos<br>shellies/shellyswitch25-1099CC/temperature |
| `shellyswitch25-1099F3` | Küche, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-1099F3/roller/0/command/pos<br>shellies/shellyswitch25-1099F3/roller/0/pos<br>shellies/shellyswitch25-1099F3/temperature |
| `shellyswitch25-109DA4` | Badezimmer Gäste, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-109DA4/roller/0/command<br>shellies/shellyswitch25-109DA4/roller/0/pos<br>shellies/shellyswitch25-109DA4/temperature |
| `shellyswitch25-109F0B` | Küche, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-109F0B/roller/0/command/pos<br>shellies/shellyswitch25-109F0B/roller/0/pos<br>shellies/shellyswitch25-109F0B/temperature |
| `shellyswitch25-10A070` | Jans Zimmer, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-10A070/roller/0/command<br>shellies/shellyswitch25-10A070/roller/0/pos<br>shellies/shellyswitch25-10A070/temperature |
| `shellyswitch25-10A1DE` | Schlafzimmer, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-10A1DE/roller/0/command<br>shellies/shellyswitch25-10A1DE/roller/0/pos<br>shellies/shellyswitch25-10A1DE/temperature |
| `shellyswitch25-10A277` | Shellys, Wohnzimmer | mqtt in, mqtt out | shellies/shellyswitch25-10A277/roller/0/command<br>shellies/shellyswitch25-10A277/roller/0/pos<br>shellies/shellyswitch25-10A277/temperature |
| `shellyswitch25-F37585` | Arbeitszimmer, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-F37585/roller/0/command<br>shellies/shellyswitch25-F37585/roller/0/pos<br>shellies/shellyswitch25-F37585/temperature |
| `shellyswitch25-F3FDC4` | Schlafzimmer, Shellys | mqtt in, mqtt out | shellies/shellyswitch25-F3FDC4/roller/0/command<br>shellies/shellyswitch25-F3FDC4/roller/0/pos<br>shellies/shellyswitch25-F3FDC4/temperature |

## Aktuell im LAN gefundene Jalousien-Shellys

| IP | Name/ID | Modell | Topic-ID-Hinweis |
|---|---|---|---|
| `192.168.178.24` | SHSW-25 | SHSW-25 | `shellyswitch25-1097AB` |
| `192.168.178.26` | SHSW-25 | SHSW-25 | `shellyswitch25-1099F3` |
| `192.168.178.28` | SHSW-25 | SHSW-25 | `shellyswitch25-10986E` |
| `192.168.178.30` | SHSW-25 | SHSW-25 | `shellyswitch25-10A277` |
| `192.168.178.31` | SHSW-25 | SHSW-25 | `shellyswitch25-109899` |
| `192.168.178.33` | SHSW-25 | SHSW-25 | `shellyswitch25-109DA4` |
| `192.168.178.37` | SHSW-25 | SHSW-25 | `shellyswitch25-F3FDC4` |
| `192.168.178.52` | Wohnzimmer-Rollo2 | S4SW-002P16EU | `shelly2pmg4-58e6c530408c` |
| `192.168.178.56` | Arbeitszimmer-Rollo2 | S4SW-002P16EU | `shelly2pmg4-48f6eedad190` |
| `192.168.178.59` | Kueche-Rollo1 | S4SW-002P16EU | `shelly2pmg4-58e6c5324770` |
| `192.168.178.177` | Badezimmer  | SNSW-102P16EU | `shellyplus2pm-ecc9ffc14310` |
| `192.168.178.196` | shelly2pmg4-e8f60a60b50c | S4SW-002P16EU | `shelly2pmg4-e8f60a60b50c` |

## Risiken beim direkten Import

- Viele `bigtimer`-Nodes sind aktiv und könnten beim Import/Deploy sofort Jalousien oder Außenlicht schalten.
- Der alte MQTT-Broker heißt `smarthome`; in Docker/Node-RED sollte er auf `192.168.178.40` zeigen.
- Einige alte Topic-IDs existieren aktuell vermutlich nicht mehr oder wurden durch neue Shellys ersetzt.
- Tesla-, FritzBox-, InfluxDB-, E-Mail- und Home-Assistant-Nodes benötigen Zusatzpakete und Credentials.
- `Backup MyPi` führt `sudo raspiBackup.sh` aus; diesen Tab nicht ungeprüft aktivieren.
