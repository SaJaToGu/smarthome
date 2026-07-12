# Siri-/iPhone-Steuerung für Jalousien

## Umsetzung (aktiv seit 12.07.2026)

Die Rollo-Steuerung läuft über einen zentralen HTTP-Endpoint in Node-RED:

```
http://192.168.178.40:1880/rollo?room=<raum>&pos=<0-100>
http://192.168.178.40:1880/rollo?room=<raum>&action=<stop>
```

## Architektur

```text
Siri / Apple Kurzbefehl
  → HTTP-Request im Heimnetz
  → Node-RED /rollo Endpoint
  → MQTT / Shelly Gen1 oder RPC (Gen2/4)
  → Jalousie

WhatsApp/Telegram
  → Hermes Gateway
  → Hermes Skill "rollo-steuerung"
  → curl → Node-RED /rollo → MQTT → Shelly

Alexa (später)
  → Alexa Skill → HTTPS → Node-RED (nur mit VPN/sicherem Tunnel)
```

## Befehle

| Sprachbefehl | Endpoint |
|---|---|
| „Wohnzimmer Rollos hoch" | `/rollo?room=wohnzimmer&pos=100` |
| „Küche Jalousien runter" | `/rollo?room=kueche&pos=0` |
| „Erdgeschoss Rollos 50%" | `/rollo?room=eg&pos=50` |
| „Alle Rollos stopp" | `/rollo?room=alle&action=stop` |
| „Schlafzimmer zu" | `/rollo?room=schlafzimmer&action=zu` |

## Verfügbare Räume/Etagen

| Befehl | Betroffene Rollos |
|---|---|
| `kueche` | Küche1 + Küche2 |
| `wohnzimmer` | Wohnzimmer1 + Wohnzimmer2 |
| `schlafzimmer` | Schlafzimmer1-3 |
| `arbeitszimmer` | Arbeitszimmer1 + Arbeitszimmer2 |
| `gaestebad` | Gästebad |
| `badezimmer` | Badezimmer |
| `till`, `jan` | Einzelne Rollos 2. OG |
| `eg` / `erdgeschoss` | Küche1-2, Gästebad, Wohnzimmer1-2 |
| `1og` / `obergeschoss` | Schlafzimmer1-3, Arbeitszimmer1-2, Badezimmer |
| `2og` / `dachgeschoss` | Till, Jan |
| `alle` | Alle 13 Rollos |

## Siri-Kurzbefehl einrichten

1. **Apple Kurzbefehle-App** öffnen
2. Neuer Kurzbefehl → **„URL"**-Aktion hinzufügen
3. URL: `http://192.168.178.40:1880/rollo?room=wohnzimmer&pos=100`
4. **„Inhalte von URL abrufen"**-Aktion hinzufügen (Methode: GET)
5. Kurzbefehl benennen: z.B. „Wohnzimmer Rollos hoch"
6. Mit Siri: „Hey Siri, Wohnzimmer Rollos hoch"

**Wichtig:** Das iPhone muss im Heimnetz sein (WLAN). Von unterwegs nur per VPN (Tailscale).

## Hermes (Telegram / WhatsApp)

Der Skill `rollo-steuerung` ist unter `~/.hermes/skills/smart-home/rollo-steuerung/`
installiert. Hermes erkennt natürliche Befehle wie:

- „Mach die Rollos im Wohnzimmer runter"
- „Erdgeschoss Jalousien auf 50%"
- „Stopp alle Rollos"

und führt sie über den Node-RED-Endpoint aus.

## Sicherheit

- Endpoint nur im Heimnetz erreichbar (192.168.178.40:1880)
- Kein offener Internet-Port
- State-Tracking verhindert Zurückstellen manueller Änderungen
- Küche1/2 nie ganz schließen (Blumen, min. 20%)