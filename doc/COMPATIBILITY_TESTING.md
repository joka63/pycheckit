# Kompatibilitätstests mit dem originalen checkit

## Übersicht

Die Test-Suite in `testing/test_cli.py` enthält eine spezielle Testklasse `TestCheckitCompatibility`, die die Kompatibilität zwischen `pycheckit` und dem originalen `checkit` überprüft.

## Voraussetzungen

Die Kompatibilitätstests werden nur ausgeführt, wenn das originale `checkit` im `PATH` verfügbar ist. Falls `checkit` nicht installiert ist, werden diese Tests automatisch übersprungen.

## Durchgeführte Tests

Die folgenden Kompatibilitätstests werden durchgeführt:

### 1. CRC-Wert-Kompatibilität (`test_store_compatibility`)
Überprüft, dass beide Tools den gleichen CRC64-Wert für dieselbe Datei berechnen und speichern.

### 2. Gegenseitige Verifizierung - pycheckit speichert (`test_check_compatibility_pycheckit_store`)
Überprüft, dass `checkit` einen von `pycheckit` gespeicherten CRC erfolgreich verifizieren kann.

### 3. Gegenseitige Verifizierung - checkit speichert (`test_check_compatibility_checkit_store`)
Überprüft, dass `pycheckit` einen von `checkit` gespeicherten CRC erfolgreich verifizieren kann.

### 4. Anzeige-Kompatibilität (`test_display_compatibility`)
Überprüft, dass beide Tools den gleichen CRC-Wert anzeigen (Option `-p`).

### 5. Lösch-Kompatibilität (`test_remove_compatibility`)
Überprüft, dass beide Tools CRC-Attribute entfernen können, die vom jeweils anderen Tool erstellt wurden.

### 6. Export/Import-Kompatibilität (`test_export_import_compatibility`)
Überprüft bidirektionale Kompatibilität für Export und Import:
- `pycheckit` exportiert → `checkit` importiert
- `checkit` exportiert → `pycheckit` importiert

### 7. Ausgabeformat-Kompatibilität (`test_output_format_compatibility`)
Überprüft, dass beide Tools ein ähnliches Ausgabeformat verwenden (insbesondere "OK" bei erfolgreicher Verifizierung).

## Tests ausführen

Alle Kompatibilitätstests ausführen:
```bash
uv run pytest testing/test_cli.py::TestCheckitCompatibility -v
```

Einzelnen Test ausführen:
```bash
uv run pytest testing/test_cli.py::TestCheckitCompatibility::test_store_compatibility -v
```

Alle CLI-Tests (inklusive Kompatibilitätstests):
```bash
uv run pytest testing/test_cli.py -v
```

## Erwartete Ergebnisse

Bei installiertem `checkit`:
- Alle 7 Kompatibilitätstests sollten erfolgreich sein
- Dies bestätigt vollständige Kompatibilität zwischen beiden Tools

Ohne `checkit`:
- Die Tests werden übersprungen (SKIPPED)
- Die anderen CLI-Tests laufen normal durch

## Technische Details

Die Tests verwenden:
- `subprocess.run()` zum Aufrufen der CLI-Tools
- Temporäre Verzeichnisse für isolierte Tests
- Direkte Überprüfung der extended attributes mit `get_crc()`
- Vergleich der Ausgaben beider Tools

## Bedeutung

Diese Tests stellen sicher, dass `pycheckit` als vollständig kompatible Reimplementierung von `checkit` funktioniert und als Drop-In-Ersatz verwendet werden kann.

