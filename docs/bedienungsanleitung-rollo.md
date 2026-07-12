# Rollo-Steuerung – Bedienungsanleitung

Stand: 13.07.2026

## Überblick

Alle 13 Jalousien im Haus lassen sich per Sprache, Chat oder App steuern. Die
Solar-Automatik läuft im Hintergrund und sorgt für Beschattung nach Sonnenstand.

| Was | Wann |
|---|---|
| 🌅 Morgens (Sonnenauf–Mittag) | Ostseite wird bei starker Sonne beschattet |
| ☀️ Nachmittags (Mittag–Sonnunter) | Westseite wird bei starker Sonne beschattet |
| 🌙 Nachts | Alle Rollos schließen |
| 💡 Außenlicht | Abends an, nachts aus, morgens bei Bewölkung an |

---

## Steuerung per Sprache/Chat

### Siri (iPhone)

1. Kurzbefehl in der „Kurzbefehle"-App anlegen
2. URL: `http://192.168.178.40:1880/rollo?room=…&action=…`
3. Mit „Hey Siri, …" aktivieren

**Funktioniert nur im Heim-WLAN!** Von unterwegs nur mit VPN (Tailscale).

### Telegram / WhatsApp

Einfach eine Nachricht an Hermes schicken, z. B.:

- „Mach die Rollos im Wohnzimmer runter"
- „Erdgeschoss beschatten"
- „Alle Jalousien stopp"

Hermes erkennt den Befehl automatisch und führt ihn aus.

---

## Verfügbare Befehle

### Aktionen

| Befehl | Bedeutung |
|---|---|
| `auf`, `hoch`, `rauf`, `öffnen` | Ganz öffnen (100%) |
| `zu`, `runter`, `schließen` | Ganz schließen (0%) |
| `beschatten`, `schatten`, `sonnenschutz` | Halbschatten (50%) |
| `stop`, `stopp`, `halt` | Anhalten |
| Eine Zahl (z. B. `30`, `75`) | Auf genaue Prozentposition fahren |

### Räume einzeln

| Name | Rollos |
|---|---|
| `küche` | Küche 1 + 2 |
| `wohnzimmer` | Wohnzimmer 1 + 2 |
| `schlafzimmer` | Schlafzimmer 1–3 |
| `arbeitszimmer` | Arbeitszimmer 1 + 2 |
| `gästebad`, `gaestebad` | Gästebad |
| `badezimmer` | Badezimmer (1. OG) |
| `till` | Till (2. OG) |
| `jan` | Jan (2. OG) |

### Etagen

| Name | Rollos |
|---|---|
| `eg`, `erdgeschoss` | Küche 1+2, Gästebad, Wohnzimmer 1+2 |
| `1og`, `obergeschoss` | Schlafzimmer 1–3, Arbeitszimmer 1+2, Badezimmer |
| `2og`, `dachgeschoss` | Till, Jan |
| `alle` | Alle 13 Rollos |

### Himmelsrichtungen

| Name | Rollos |
|---|---|
| `ost`, `osten` | Küche 2, Gästebad, Badezimmer, Arbeitszimmer 2 |
| `west`, `westen` | Wohnzimmer 1+2, Schlafzimmer 1+2 |
| `nord`, `norden` | Küche 1, Schlafzimmer 3, Arbeitszimmer 1, Till, Jan |

### Beispiele

| Sprachbefehl | Endpoint |
|---|---|
| „Wohnzimmer Rollos runter" | `/rollo?room=wohnzimmer&action=zu` |
| „Erdgeschoss beschatten" | `/rollo?room=eg&action=beschatten` |
| „Küche Jalousien 30%" | `/rollo?room=kueche&pos=30` |
| „Alle Rollos stopp" | `/rollo?room=alle&action=stop` |
| „Westen Rollos hoch" | `/rollo?room=west&pos=100` |
| „Osten beschatten" | `/rollo?room=ost&action=beschatten` |

---

## Automatik-Regeln

- **Ostseite** (Küche2, Gästebad, Badezimmer, Arbeitszimmer2) wird ab Sonnenaufgang
  beschattet, sobald die Solarleistung 2500 W übersteigt.
- **Westseite** (Wohnzimmer1–2, Schlafzimmer1–2) wird ab Sonnenhöchststand beschattet.
- **Nordseite** (Küche1, Schlafzimmer3, Arbeitszimmer1, Till, Jan) wird nie automatisch
  beschattet.
- Die Beschattung löst sich, wenn die PV-Leistung unter 1200 W fällt (Hysterese).
- Schlafzimmer werden am Wochenende nicht automatisch beschattet (nur Zeitplan).
- Werktags öffnen Schlafzimmer nicht vor 7:00 Uhr.
- Nachts schließen alle Rollos (Küche 1+2 nur auf 20% – Blumen auf Fensterbank).
- **Wichtig:** Manuelle Befehle werden nicht überschrieben. Das System merkt sich die
  letzte Position und sendet nur bei Änderung.

---

## Was tun, wenn…

- **…ein Rollo nicht reagiert?** → Im Node-RED unter `http://192.168.178.40:1880`
  im Tab „Solar-Beschattung Jalousien" die Debug-Seitenleiste prüfen.
- **…die Beschattung zu stark/schwach ist?** → `shadePos` (aktuell 50%) im
  Solar-Flow oder im `/rollo`-Endpoint anpassen.
- **…ein Rollo falsch positioniert ist?** → Shelly-Kalibrierung:
  `curl http://<ip>/roller/0/calibrate` (Gen1) oder per RPC (Gen2/4).
- **…manuelle Änderung wird zurückgesetzt?** → Der Flow speichert den letzten
  gesendeten Wert. Nach einem Node-RED-Neustart wird einmalig alles neu gesetzt.
- **…Außenlicht geht nicht?** → Shelly1-E098068CC9EB (192.168.178.35) prüfen.

---

## Technische Referenz

### Shelly-Übersicht

| Raum | ID | IP | Typ |
|---|---|---|---|
| Küche 1 | `shelly2pmg4-58e6c5324770` | .59 | Gen4 RPC |
| Küche 2 | `shellyswitch25-1099F3` | .26 | Gen1 |
| Gästebad | `shellyswitch25-109DA4` | .33 | Gen1 |
| Wohnzimmer 1 | `shellyswitch25-10A277` | .30 | Gen1 |
| Wohnzimmer 2 | `shelly2pmg4-58e6c530408c` | .52 | Gen4 RPC |
| Schlafzimmer 1 | `shellyswitch25-F3FDC4` | .37 | Gen1 |
| Schlafzimmer 2 | `shellyswitch25-10A1DE` | .50 | Gen1 |
| Schlafzimmer 3 | `shellyswitch25-1097AB` | .24 | Gen1 |
| Arbeitszimmer 1 | `shellyswitch25-10986E` | .28 | Gen1 |
| Arbeitszimmer 2 | `shelly2pmg4-48f6eedad190` | .56 | Gen4 RPC |
| Badezimmer | `shellyplus2pm-ecc9ffc14310` | .177 | Gen2 RPC |
| Till | `shellyswitch25-109899` | .31 | Gen1 |
| Jan | `shelly2pmg4-e8f60a60b50c` | .196 | Gen4 RPC |
| Außenlicht | `shelly1-E098068CC9EB` | .35 | Gen1 |

### Links

- Node-RED: `http://192.168.178.40:1880` (admin / Passwort in `.secrets/`)
- Grafana: `http://192.168.178.40:3000`
- MQTT-Broker: `192.168.178.40:1883`