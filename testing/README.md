# PyCheckit Test Suite

Dieses Verzeichnis enthält die pytest-basierten Unit-Tests für pycheckit.

## Test-Struktur

- `conftest.py` - Pytest-Konfiguration und gemeinsame Fixtures
- `test_crc64.py` - Tests für CRC64-Algorithmus (3 Tests)
- `test_file_list.py` - Tests für FileList-Klasse (5 Tests)
- `test_imports.py` - Tests für Modul-Importe (7 Tests)
- `test_core.py` - Integrationstests für Core-Funktionalität (9 Tests)
- `test_cli.py` - Tests für Command-Line-Interface (5 Tests)

**Gesamt: 29 Tests**

## Tests ausführen

```bash
# Alle Tests ausführen (empfohlen)
make test

# Direkt mit pytest
pytest testing/

# Mit Verbose-Modus
pytest -v testing/

# Bestimmte Test-Datei
pytest testing/test_crc64.py

# Bestimmten Test
pytest testing/test_crc64.py::TestCRC64::test_crc64_known_vector

# Mit Coverage-Report
pytest --cov=pycheckit testing/

# Coverage mit HTML-Report
pytest --cov=pycheckit --cov-report=html testing/
```

## Fixtures

Die `conftest.py` stellt folgende Fixtures bereit:

- `temp_file` - Temporäre Testdatei, wird nach dem Test automatisch gelöscht
- `temp_dir` - Temporäres Verzeichnis, wird nach dem Test automatisch gelöscht

## Test-Kategorien

### Unit-Tests
- **test_crc64.py** - Testet den CRC64-Algorithmus isoliert
- **test_file_list.py** - Testet die FileList-Klasse
- **test_imports.py** - Stellt sicher, dass alle Module importierbar sind

### Integrationstests
- **test_core.py** - Testet die Core-Funktionalität mit echten Dateien
- **test_cli.py** - Testet die CLI-Schnittstelle End-to-End

