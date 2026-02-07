# Test-Migration zu pytest

## Durchgeführte Änderungen

### 1. Neue Test-Struktur
- Alle Tests wurden in das neue Verzeichnis `testing/` verschoben
- Alte Test-Dateien aus dem Root-Verzeichnis entfernt:
  - `test_basic.py`
  - `test_debug.py`
  - `test_e2e.py`
  - `test_integration.py`

### 2. Neue pytest-basierte Tests

Das `testing/` Verzeichnis enthält jetzt:

- **`conftest.py`** - Pytest-Konfiguration mit gemeinsamen Fixtures:
  - `temp_file` - Temporäre Testdatei
  - `temp_dir` - Temporäres Verzeichnis

- **`test_crc64.py`** - Unit-Tests für CRC64-Algorithmus (3 Tests)
  - Test mit bekanntem Testvektor
  - Test mit leeren Daten
  - Test für inkrementelle Berechnung

- **`test_file_list.py`** - Unit-Tests für FileList-Klasse (5 Tests)
  - Erstellung, Hinzufügen, Ausgabe

- **`test_imports.py`** - Tests für Modul-Importe (7 Tests)
  - Stellt sicher, dass alle Module importierbar sind

- **`test_core.py`** - Integrationstests für Core-Funktionalität (9 Tests)
  - CRC-Operationen (berechnen, speichern, abrufen, entfernen)
  - Export/Import-Funktionalität

- **`test_cli.py`** - Tests für Command-Line-Interface (5 Tests)
  - CLI-Kommandos (store, check, remove, export, import)

**Gesamt: 29 Tests** - alle bestehen ✅

### 3. Konfigurationsänderungen

**pyproject.toml:**
- Dev-Abhängigkeiten hinzugefügt: `pytest>=7.0`, `pytest-cov>=4.0`
- pytest-Konfiguration hinzugefügt unter `[tool.pytest.ini_options]`

**Makefile:**
- `.venv` Target installiert jetzt auch dev-Abhängigkeiten
- `test` Target nutzt das neue `testing/` Verzeichnis

**.gitignore:**
- Bereits optimiert, passt für die neue Struktur

### 4. Aufräumen
- Alte Python-Dateien aus dem Root-Verzeichnis entfernt:
  - `pycheckit.py`, `pycheckit_cli.py`, `crc64.py`, `file_list.py`, `main.py`
- Diese Dateien blockierten den Import des `pycheckit`-Packages

## Tests ausführen

```bash
# Alle Tests
make test

# Oder direkt mit pytest
pytest testing/

# Mit Coverage
pytest --cov=pycheckit testing/

# Einzelner Test
pytest testing/test_crc64.py::TestCRC64::test_crc64_known_vector
```

## Nach git clone

```bash
git clone <repository>
cd pycheckit
make build    # Erstellt .venv mit dev-Abhängigkeiten und baut das Paket
make test     # Führt alle Tests aus
```

