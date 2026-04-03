# Contributing

## Setup

```bash
git clone https://github.com/noredgaras/mvt_parser_lib.git
cd mvt_parser_lib

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -e .
pip install pytest ruff
```

## Running tests

```bash
# All tests
pytest tests/

# Single test
pytest tests/test_parser.py::test_departure_message
```

## Linting

```bash
ruff check mvt_parser/
ruff check mvt_parser/ --fix
```

## Project structure

```
mvt_parser/
    __init__.py     exports
    parser.py       MVTParser — all parsing logic
    models.py       dataclasses: MVTMessage, FlightLeg, MovementTime, Delay, PassengerInfo
    exceptions.py   MVTParseError
tests/
    test_parser.py
examples/
    run_parser.py
```

## Making changes

- Parser logic lives entirely in `parser.py`
- All new tokens should be handled in `_parse_line()` and covered by a test
- `MVTParseError` should be raised for any malformed input — never silently ignore

## Submitting a PR

1. Fork the repo and create a branch
2. Make your changes with tests
3. Run `pytest tests/` and `ruff check mvt_parser/` — both must pass
4. Open a pull request with a description of what changed and why
