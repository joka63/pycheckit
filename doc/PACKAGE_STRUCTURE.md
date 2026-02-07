# pycheckit - Python Package Structure

## Zusammenfassung der Reorganisation

Das pycheckit-Projekt wurde erfolgreich in eine professionelle Python-Paketstruktur reorganisiert, die mit `uv build` und anderen Standard-Build-Tools kompatibel ist.

## Neue Struktur

```
pycheckit/
├── src/
│   └── pycheckit/              # Hauptpaket
│       ├── __init__.py         # Paket-Initialisierung, exportiert main()
│       ├── __main__.py         # Ermöglicht: python -m pycheckit
│       ├── cli.py              # Kommandozeilen-Interface mit argparse
│       ├── core.py             # Kernfunktionalität (CRC-Operationen)
│       ├── constants.py        # Alle Konstanten und Enums
│       ├── crc64.py            # CRC64-Implementierung
│       └── file_list.py        # Dateiverwaltung
├── dist/                       # Build-Artefakte (von .gitignore ausgeschlossen)
│   ├── pycheckit-0.5.2-py3-none-any.whl
│   └── pycheckit-0.5.2.tar.gz
├── pyproject.toml              # Moderne Python-Projektkonfiguration
├── Makefile                    # Convenience-Befehle
├── DEVELOPMENT.md              # Entwicklerdokumentation
├── .gitignore                  # Git-Ignore-Datei
└── README.md                   # Hauptdokumentation
```

## Verwendung des Makefiles

Das Makefile bietet folgende Befehle:

```bash
make help       # Hilfe anzeigen
make build      # Paket bauen (erstellt .whl und .tar.gz in dist/)
make install    # Paket installieren
make dev        # Im Entwicklungsmodus installieren
make clean      # Build-Artefakte löschen
make test       # Tests ausführen
make format     # Code formatieren
make lint       # Code-Qualität prüfen
make check      # Alle Prüfungen ausführen
```

## Paket bauen

```bash
# Mit Makefile (empfohlen)
make build

# Mit uv direkt
uv build

# Mit Python build
python3 -m build
```

Dies erstellt:
- `dist/pycheckit-0.5.2-py3-none-any.whl` - Wheel-Distribution
- `dist/pycheckit-0.5.2.tar.gz` - Source-Distribution

## Installation

```bash
# Aus lokalem Build
pip install dist/pycheckit-0.5.2-py3-none-any.whl

# Entwicklungsmodus
make dev
# oder
pip install -e .
```

## Verwendung nach Installation

```bash
# Als Kommando (nach Installation)
pycheckit -s datei.txt

# Als Modul
python3 -m pycheckit -s datei.txt

# In Python-Code
from pycheckit import main
```

## Vorteile der neuen Struktur

1. **Standard-konform**: Folgt PEP 518 und modernen Python-Packaging-Standards
2. **src-Layout**: Verhindert versehentliche Imports aus dem Projektverzeichnis
3. **Modular**: Code ist in logische Module aufgeteilt:
   - `constants.py` - Alle Konstanten an einem Ort
   - `core.py` - Kernfunktionalität
   - `cli.py` - CLI-spezifischer Code
4. **Build-freundlich**: Funktioniert mit uv, pip, build und anderen Tools
5. **Entry-Points**: Definiert in `pyproject.toml`, erstellt automatisch `pycheckit` Befehl
6. **Makefile**: Vereinfacht häufige Entwicklungsaufgaben

## pyproject.toml Highlights

```toml
[project.scripts]
pycheckit = "pycheckit.cli:main"  # Erstellt pycheckit Befehl

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Nächste Schritte

1. Tests in das neue Struktur-Layout migrieren
2. Optional: CI/CD mit GitHub Actions einrichten
3. Optional: Auf PyPI veröffentlichen mit `uv publish`

## Migration von alten Dateien

Die ursprünglichen Dateien im Root-Verzeichnis können nun entfernt werden:
- `pycheckit.py` → `src/pycheckit/cli.py` und `src/pycheckit/core.py`
- `crc64.py` → `src/pycheckit/crc64.py`
- `file_list.py` → `src/pycheckit/file_list.py`
- `main.py` und `pycheckit_cli.py` → nicht mehr benötigt

