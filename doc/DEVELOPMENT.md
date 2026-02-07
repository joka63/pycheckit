# pycheckit - Development Guide

## Projektstruktur

Das Projekt folgt einem modernen Python-Paket-Layout:

```
pycheckit/
├── src/
│   └── pycheckit/
│       ├── __init__.py      # Paket-Initialisierung
│       ├── cli.py           # Kommandozeilen-Interface
│       ├── core.py          # Kernfunktionalität
│       ├── constants.py     # Konstanten und Enums
│       ├── crc64.py         # CRC64-Implementierung
│       └── file_list.py     # Dateiverwaltung
├── pyproject.toml           # Projekt-Konfiguration
├── Makefile                 # Build-Automatisierung
└── README.md                # Projektdokumentation
```

## Installation

### Mit uv (empfohlen)

```bash
# Entwicklungsmodus
make dev
# oder
uv pip install -e .

# Normale Installation
make install
# oder
uv pip install .
```

### Mit pip

```bash
# Entwicklungsmodus
pip install -e .

# Normale Installation
pip install .
```

## Paket bauen

### Mit Make

```bash
make build
```

Dies führt folgende Schritte aus:
1. Löscht alte Build-Artefakte
2. Baut das Paket mit `uv build`
3. Erstellt Distribution-Dateien in `dist/`

### Manuell mit uv

```bash
uv build
```

Dies erstellt:
- `dist/pycheckit-0.5.2-py3-none-any.whl` (Wheel)
- `dist/pycheckit-0.5.2.tar.gz` (Source Distribution)

## Makefile-Befehle

- `make help` - Zeigt verfügbare Befehle
- `make build` - Baut das verteilbare Paket
- `make install` - Installiert das Paket
- `make dev` - Installiert im Entwicklungsmodus
- `make clean` - Löscht Build-Artefakte und Caches
- `make test` - Führt Tests aus
- `make format` - Formatiert Code mit black
- `make lint` - Prüft Code mit ruff und mypy
- `make check` - Führt alle Prüfungen aus

## Entwicklung

### Voraussetzungen

- Python >= 3.12
- uv (empfohlen) oder pip
- xattr-Bibliothek

### Dependencies installieren

```bash
uv pip install -e ".[dev]"
```

### Tests ausführen

```bash
make test
```

### Code formatieren

```bash
make format
```

### Code-Qualität prüfen

```bash
make lint
```

## Paket veröffentlichen

Nach dem Bauen können die Dateien in `dist/` auf PyPI hochgeladen werden:

```bash
# Mit uv
uv publish

# Mit twine
twine upload dist/*
```

## Modul-Beschreibungen

### `cli.py`
Enthält die Hauptlogik für die Kommandozeilenanwendung:
- Argument-Parsing mit `argparse`
- Datei- und Verzeichnisverarbeitung
- Ausgabeformatierung

### `core.py`
Kernfunktionalität für CRC-Operationen:
- CRC-Berechnung und -Speicherung
- Extended Attributes-Verwaltung
- Fehlerbehandlung

### `constants.py`
Definiert alle Konstanten:
- Fehlertypen
- Flags
- Farbdefinitionen
- Dateisystem-Konstanten

### `crc64.py`
CRC64-Implementierung:
- Jones-Koeffizienten
- Optimierte Lookup-Tabelle

### `file_list.py`
Hilfsfunktionen für Dateilisten-Verwaltung

## Lizenz

GPL-3.0-or-later

