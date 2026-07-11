# Solarbasierte Jalousie-Beschattung

## Ziel

Die Solaranlage/SENEC wird als praktischer Sonnendetektor genutzt. Wenn die PV-Anlage stark produziert, ist mit direkter Sonneneinstrahlung zu rechnen. Dann wird abhängig von Uhrzeit/Hausseite beschattet.

## Read-only SENEC-Abfrage

Die bestehende SENEC-API unter `192.168.178.121` wurde read-only abgefragt:

```text
POST https://192.168.178.121/lala.cgi
Payload: {"ENERGY":{}}
```

Das Gerät verwendet ein lokales/self-signed HTTPS-Zertifikat. Für die lokale Node-RED-Abfrage ist deshalb ein TLS-Config-Node mit deaktivierter Serverzertifikatsprüfung nötig.

Beobachtete Felder:

| SENEC-Feld | Bedeutung für uns |
|---|---|
| `GUI_INVERTER_POWER` | PV-/Wechselrichterleistung in W — Hauptwert für Sonnenerkennung |
| `GUI_HOUSE_POW` | Hausverbrauch in W |
| `GUI_GRID_POW` | Netzbezug/Einspeisung in W |
| `GUI_BAT_DATA_POWER` | Batterie-Leistung in W |
| `GUI_BAT_DATA_FUEL_CHARGE` | Batterie-Ladestand in % |

Beispiel einer echten Abfrage am Abend:

| Wert | Dekodiert |
|---|---:|
| `GUI_INVERTER_POWER` | ca. `2058 W` |
| `GUI_HOUSE_POW` | ca. `1774 W` |
| `GUI_GRID_POW` | ca. `11 W` |
| `GUI_BAT_DATA_POWER` | ca. `295 W` |
| `GUI_BAT_DATA_FUEL_CHARGE` | ca. `99 %` |

## Beschattungsgruppen

### Ostseite — morgens

Bei starker Sonne morgens auf ca. 50 %:

| Rollo | IP | MQTT/Topic-Hinweis |
|---|---|---|
| Küche2 | `192.168.178.26` | `shellies/shellyswitch25-1099F3/...` |
| GästeBad | `192.168.178.33` | `shellies/shellyswitch25-109DA4/...` |
| Badezimmer | `192.168.178.177` | `shellyplus2pm-ecc9ffc14310/rpc` |
| Arbeitszimmer2 | `192.168.178.56` | `shelly2pmg4-48f6eedad190/rpc` |

### Westseite — ab ca. 13:00 Uhr

Bei starker Sonne nachmittags auf ca. 50 %:

| Rollo | IP | MQTT/Topic-Hinweis |
|---|---|---|
| Schlafzimmer1 | `192.168.178.37` | `shellies/shellyswitch25-F3FDC4/...` |
| Schlafzimmer2 | `192.168.178.50` | `shellies/shellyswitch25-10A1DE/...` |
| Wohnzimmer1 | `192.168.178.30` | `shellies/shellyswitch25-10A277/...` |
| Wohnzimmer2 | `192.168.178.52` | `shelly2pmg4-58e6c530408c/rpc` |

## Startlogik

Bewusst konservative Startwerte:

| Parameter | Startwert | Zweck |
|---|---:|---|
| Beschattung aktiv ab | `2500 W` PV-Leistung | starke direkte Sonne erkannt |
| Beschattung lösen unter | `1200 W` PV-Leistung | später für Hysterese |
| Ostphase | `07:00–13:00` | Ostseite beobachten |
| Westphase | `13:00–20:30` | Westseite beobachten |
| Zielposition Beschattung | `50 %` | beschatten, aber nicht komplett dunkel |
| Zufallsversatz je Rollo | `30 s–8 min` | natürliches Verhalten |

## Vorbereiteter Node-RED-Flow

Datei:

```text
imports/jalousien-solar-beschattung.DRAFT-DISABLED.json
```

Zusätzlich ist der Flow in `nodered/data/flows.json` vorbereitet, aber der Tab ist deaktiviert:

```text
ENTWURF Solar-Beschattung Jalousien
```

Der Entwurf:

- fragt SENEC read-only ab,
- dekodiert die Solarwerte,
- entscheidet Ost-/Westphase,
- erzeugt nur einen Debug-Beschattungsplan,
- enthält **keine angeschlossenen MQTT-Ausgänge für Rollo-Bewegung**.

## Nächste Schritte vor Aktivierung

1. Node-RED neu starten und prüfen, dass der deaktivierte Tab keine Aktionen auslöst.
2. Debug-Plan einmal manuell prüfen.
3. Positionskommandos je Rollo einzeln testen.
4. Hysterese und manuelle Override-Logik ergänzen.
5. Erst danach MQTT-Ausgänge mit Zufallsversatz anschließen.
