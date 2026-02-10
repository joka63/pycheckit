# Bekannte Bugs in pycheckit

## Bug #1: Fehlende Fehlermeldung bei nicht existierenden Dateien

### Beschreibung
Wenn `pycheckit` auf eine nicht existierende Datei angewendet wird, zeigt es keine Fehlermeldung an, während das originale `checkit` eine klare Fehlermeldung ausgibt.

### Vergleich des Verhaltens

**checkit (korrekt):**
```bash
$ checkit -s /tmp/nonexistent_file
For file /tmp/nonexistent_file: Could not open file.
Total of 0 file(s) processed.
```

**pycheckit (fehlerhaft):**
```bash
$ pycheckit -s /tmp/nonexistent_file
Total of 0 file(s) processed.
```

### Erwartetes Verhalten
- `pycheckit` sollte die gleiche Fehlermeldung wie `checkit` ausgeben
- Die Fehlermeldung sollte klar angeben, dass die Datei nicht geöffnet werden konnte
- Der Exit-Code sollte nicht 0 sein (Fehler)

### Unit-Test
Der Bug wird durch einen automatisierten Unit-Test dokumentiert:
- **Datei**: `testing/test_cli.py`
- **Test**: `TestCheckitCompatibility::test_nonexistent_file_error_message`
- **Status**: `@pytest.mark.xfail` (expected failure)

Der Test ist als "expected failure" markiert und wird automatisch erfolgreich, sobald der Bug behoben ist.

### Test ausführen

Um den Bug-Test zu sehen:
```bash
# Test mit xfail ausführen (zeigt XFAIL)
uv run pytest testing/test_cli.py::TestCheckitCompatibility::test_nonexistent_file_error_message -v

# Test ohne xfail ausführen (zeigt den tatsächlichen Fehler)
uv run pytest testing/test_cli.py::TestCheckitCompatibility::test_nonexistent_file_error_message --runxfail -v
```

### Betroffene Funktionen
- `process_file()` in `src/pycheckit/cli.py`
- Möglicherweise auch `file_crc64()` in `src/pycheckit/core.py`

### Priorität
Mittel - Beeinträchtigt die Benutzerfreundlichkeit, aber nicht die Kernfunktionalität.

### Geplante Behebung
Der Bug soll in einem späteren Schritt behoben werden. Der Unit-Test dient als Regression-Test, um sicherzustellen, dass die Behebung korrekt funktioniert.

---

## Wie man neue Bugs dokumentiert

1. **Unit-Test erstellen**: Schreiben Sie einen Test, der das erwartete Verhalten überprüft
2. **Mit @pytest.mark.xfail markieren**: Damit der Test die Test-Suite nicht zum Scheitern bringt
3. **Hier dokumentieren**: Beschreiben Sie das Problem, das erwartete Verhalten und den Workaround
4. **Nach der Behebung**: Entfernen Sie den xfail-Marker und schließen Sie diesen Eintrag

