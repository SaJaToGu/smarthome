# Jalousien und Shelly

## Status

- MQTT-Broker: `192.168.178.40:1883`
- 13 Jalousien-Shellys sind auf MQTT konfiguriert.
- Erdgeschoss-Jalousien getestet am 12.07.2026: alle drei reagieren auf MQTT-Positionskommandos.

## Geräteübersicht (getestet)

| Raum | Shelly-ID | IP | MQTT-Topic | Status |
|---|---|---|---|---|
| Küche2 | `shellyswitch25-1099F3` | 192.168.178.26 | `shellies/shellyswitch25-1099F3/roller/0/command/pos` | ✅ getestet |
| GästeBad | `shellyswitch25-109DA4` | 192.168.178.33 | `shellies/shellyswitch25-109DA4/roller/0/command/pos` | ✅ getestet (Rekalibrierung nötig) |
| Wohnzimmer1 | `shellyswitch25-10A277` | 192.168.178.30 | `shellies/shellyswitch25-10A277/roller/0/command/pos` | ✅ getestet (FRITZ!Repeater 2400 Wohnzimmer) |

### Andere bekannte Geräte

| Raum | Shelly-ID | IP | Status |
|---|---|---|---|
| Till (Schlafzimmer) | `shellyswitch25-109899` | 192.168.178.31 | nicht getestet (1. OG) |
| Schlafzimmer1 | `shellyswitch25-F3FDC4` | 192.168.178.37 | nicht getestet (1. OG) |
| Schlafzimmer2 | `shellyswitch25-10A1DE` | 192.168.178.50 | nicht getestet (1. OG) |
| Schlafzimmer3 | `shellyswitch25-1097AB` | 192.168.178.24 | nicht getestet (1. OG) |
| Jan | `shellyswitch25-10A070` | — | offline |
| Arbeitszimmer2 | `shellyswitch25-10986E` | 192.168.178.28 | nicht getestet |
| Badezimmer | `shellyswitch25-1097D5` | — | offline |
| Küche1 | `shellyswitch25-109F0B` | — | offline |
| Wohnzimmer2 | `shellyswitch25-1099CC` | — | offline |

## MQTT-Befehle

```bash
# Position setzen (0=zu, 100=offen)
mosquitto_pub -h 192.168.178.40 -t "shellies/<id>/roller/0/command/pos" -m "50"

# Kommandos: open, close, stop
mosquitto_pub -h 192.168.178.40 -t "shellies/<id>/roller/0/command" -m "open"
```

## Bekannte Probleme

- **GästeBad (109DA4):** Positions-Tracking war defekt (zeigte dauerhaft 101%). Rekalibrierung per `curl http://192.168.178.33/roller/0/calibrate` (POST) hat das behoben. Danach Vollzyklus 0%→100% gefahren.
- **Wohnzimmer2 (1099CC), Küche1 (109F0B), Jan (10A070), Badezimmer OG (1097D5):** offline, tauchen nicht im Netzwerk-Scan auf.
