# Außenlicht

## Ziel

Außenlicht über Shelly/MQTT oder vorhandene Schalter steuern.

## Benötigte Informationen

- Welche Geräte/Schalter steuern das Außenlicht?
- Shelly-IP oder MQTT-Topic
- Bewegungsmelder vorhanden?
- Gewünschte Zeit-/Sonnenstandslogik

## Geplanter Ansatz

1. Gerät identifizieren.
2. Schalten per MQTT testen.
3. Node-RED Flow für manuell/an/aus/Automatik erstellen.
4. Sonnenuntergang/Sonnenaufgang-Regeln ergänzen.
