# Raspberry-Pi Stromversorgung und SSD überwachen

## Warum

Der frühere Raspberry Pi ist regelmäßig ausgefallen. Bekannte/verdächtige Ursachen:

1. IOTstack hat den Pi täglich neu gestartet.
2. Später gab es Ausfälle auch ohne täglichen Neustart.
3. Die alte 256-GB-SSD ist gestorben.
4. Die aktuelle 32-GB-SSD ist ebenfalls älter und soll beobachtet werden.

Ziel: Frühzeitig erkennen, ob Probleme von Stromversorgung, Throttling, Temperatur, USB/SSD, Dateisystem oder unerwarteten Neustarts kommen.

## Live-Befund vom ersten Check

- Host: `metis-rpi-control`
- Root-Datenträger: `/dev/sda2` auf einer `TS32GMSA370` 32-GB-SSD
- Root-FS: ext4, `rw,noatime`
- Belegung: ca. 34 %
- Raspberry-Pi-Throttling: `throttled=0x0`
- Temperatur: ca. 52 °C
- Kerneljournal: kein akuter Unterspannungs-/Throttling-/I/O-Fehler im geprüften Zeitraum; nur ein Boot-Hinweis zu Drive Cache und ein alter `mmc1`-Hinweis.

## Watchdog-Script

Script:

```text
scripts/rpi_health_watch.py
```

Es prüft:

- `vcgencmd get_throttled`
  - aktuelle Unterspannung
  - frühere Unterspannung seit Boot
  - aktuelle/frühere Drosselung
  - Temperatur-/Softlimit
- Raspberry-Pi-Temperatur
- Root-Dateisystem read-only vs. read-write
- Root-Dateisystem-Belegung
- unerwartete Boot-ID-Änderung / Neustart
- Kerneljournal auf Muster wie:
  - undervoltage
  - throttling
  - USB reset
  - I/O error
  - ext4/filesystem errors
  - read-only remount
  - corruption
- SMART-Daten, **falls** `smartctl`/`smartmontools` installiert ist.

## Aktuelle Einschränkung

`smartctl` ist aktuell nicht installiert. Deshalb ist echtes SMART-Monitoring der SSD noch nicht aktiv. Das Script meldet das einmalig und überwacht trotzdem Kernel-/Filesystem-/USB-Fehler.

Für vollständiges SSD-Monitoring sollte später installiert werden:

```bash
sudo apt-get update
sudo apt-get install -y smartmontools
```

Danach kann geprüft werden:

```bash
sudo smartctl -a /dev/sda
sudo smartctl -d sat -a /dev/sda
```

Je nach USB-SATA-Bridge funktioniert nur eine der Varianten.

## Manueller Statuscheck

```bash
cd /home/guido/smarthome
python3 scripts/rpi_health_watch.py --status
```

## Geplantes Verhalten als Hermes-Cron

Im normalen Modus ist das Script leise:

```bash
python3 /home/guido/smarthome/scripts/rpi_health_watch.py
```

- Wenn alles gut ist: keine Ausgabe.
- Bei Warnung: Ausgabe mit konkreter Ursache, z. B. Unterspannung, Neustart, I/O-Fehler oder SMART-Auffälligkeit.

Damit eignet es sich als Hermes `no_agent` Cronjob: Nur bei Problemen wird eine Nachricht geschickt.

## Nächste Verbesserung

- `smartmontools` installieren, wenn Paketinstallation erlaubt ist.
- Optional Uptime-Kuma-Monitor ergänzen, der nur prüft, ob der Pi/Node-RED/MQTT erreichbar sind.
- Später Grafana/InfluxDB-Zeitreihe für Temperatur, Disk Usage und Throttling aufbauen.
