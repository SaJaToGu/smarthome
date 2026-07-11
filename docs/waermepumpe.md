# Wärmepumpe Monitoring

## Ziel

Betriebszustand, Temperaturen, Stromverbrauch und Effizienz der Wärmepumpe sichtbar machen.

## Benötigte Informationen

- Hersteller und Modell
- Vorhandene App/Cloud/LAN-Modul
- Verfügbare Schnittstellen: Modbus, SG-Ready, MQTT, HTTP, Hersteller-API
- Gibt es einen separaten Stromzähler?

## Geplanter Ansatz

1. Datenquelle identifizieren.
2. Messwerte nach InfluxDB schreiben.
3. Grafana-Dashboard erstellen.
4. Alarme für Fehlerzustände oder ungewöhnlichen Verbrauch einrichten.
