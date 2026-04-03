# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in editable mode (required before running tests)
pip install -e .

# Run all tests
python -m pytest tests/

# Run a single test
python -m pytest tests/test_parser.py::test_departure_message

# Run the example
python examples/run_parser.py
```

## Architecture

This is a single-module parsing library with no external dependencies.

**Parsing pipeline** (`mvt_parser/parser.py`):
- `MVTParser.parse()` splits the raw message into lines, validates and extracts the header (message type + optional COR/REV flag) and flight line (flight number, day, registration, airport) via regex, then delegates remaining lines to `_parse_line()`.
- `_parse_line()` dispatches full-line prefixes first (`SI`, `DR`, `FR`, `PX`, `DL`, `NI`), then splits remaining lines into space-separated tokens and matches each by prefix (`AD`, `AA`, `ED`, `EA`, `EB`, `RC`, `FLD`, `CRT`, `MAP`, `TOF`, `TOW`, `ZFW`). Bare 3-letter uppercase tokens are treated as IATA airport codes (`destination_airport`); anything else goes to `unknown_lines`.

**Data model** (`mvt_parser/models.py`):
- `MVTMessage` — the root output dataclass holding all parsed fields.
- `MovementTime(primary, secondary)` — represents `HHMM[/HHMM]` time pairs (e.g. `AD1200/1210`).
- `Delay(reason_codes, durations)` — delay codes are 2-digit strings; durations are 4-digit HHMM strings. The parser distinguishes them by length.
- `PassengerInfo(total, infants)` — from `PX` lines.

**Error handling**: All parse failures raise `MVTParseError` (from `mvt_parser/exceptions.py`). Time fields are validated as 4-digit (`HHMM`) or 6-digit (`DDHHMM`) strings. Numeric fields (`TOF`, `TOW`, `ZFW`, passenger counts) raise `MVTParseError` on non-integer values.

**Supported message types**: `MVT`, `MVA`, `DIV` with optional `COR` (correction) or `REV` (revision) flags on the header line.
