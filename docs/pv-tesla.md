# PV-Überschussladen Tesla

## Ziel

Tesla möglichst mit PV-Überschuss laden, ohne Netzbezug unnötig zu erhöhen.

## Benötigte Informationen

- Wechselrichter-Hersteller und Modell
- Smart-Meter/Zähler-Datenquelle
- Wallbox-Hersteller und Modell
- Soll Steuerung über Tesla API, Wallbox oder beides erfolgen?

## Geplanter Ansatz

1. PV-Erzeugung und Hausverbrauch erfassen.
2. Überschuss berechnen.
3. Ladefreigabe und Ladestrom über Node-RED steuern.
4. Sicherheitsgrenzen definieren: Mindeststrom, Batterie/Netzbezug, Sperrzeiten.
