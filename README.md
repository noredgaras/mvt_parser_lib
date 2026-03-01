# MVT Parser Library

**Python library to parse OAG/IATA MVT (Movement) flight messages.**

`mvt_parser_lib` allows you to read and interpret MVT/MVA/DIV flight movement messages, extract flight details, delays, passenger info, and all relevant expressions defined in the OAG standard.

---

## Features

* Parse **MVT, MVA, DIV** messages.
* Extract flight identification, scheduled/actual/estimated times.
* Parse **delays, passenger counts, reclearance, fuel, weights**, and other expressions.
* Handles **corrections (COR) and revisions (REV)**.
* Easy-to-use Python API.
* Ready for **unit testing, CI/CD, and PyPI deployment**.

---

## Installation

Recommended: use a virtual environment:

```bash
# Navigate to project folder
cd mvt_parser_lib

# Create a virtual environment (WSL/Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# Or Windows
# python -m venv venv
# venv\Scripts\activate

# Install locally in editable mode
pip install -e .
```

---

## Usage

```python
from mvt_parser import MVTParser

raw_msg = """
MVT
BA100/27.PPVMU.LTN
AD1200/1210 EA1300 CDG
DL72/0015/0020
PX145/12
RC0945 LHR
FLD27
CRT0800
TOF6400
"""

parser = MVTParser()
msg = parser.parse(raw_msg)

# Access parsed data
print(msg.flight_number)          # BA100
print(msg.actual_departure)       # MovementTime(primary='1200', secondary='1210')
print(msg.passenger_info.total)   # 145
```

---

## Available Parsed Fields

* **Flight Info:** `flight_number`, `scheduled_day`, `aircraft_registration`, `airport_of_movement`
* **Times:** `actual_departure`, `actual_arrival`, `estimated_departure`, `estimated_arrival`, `estimated_onblock`
* **Delays:** `delays` (reason codes and durations)
* **Passenger Info:** `passenger_info` (total passengers, infants)
* **Reclearance:** `reclearance`
* **Flight Leg / Crew:** `flight_leg_date`, `crew_report_time`
* **Aircraft Weights / Fuel:** `takeoff_fuel`, `takeoff_weight`, `zero_fuel_weight`
* **Other / Unknown lines:** `unknown_lines`

---

## Testing

Run unit tests with **pytest**:

```bash
# Make sure virtual environment is activated
pytest tests
```

---

## Development

* Use `pip install -e .` for editable mode while developing.
* Run examples in `examples/run_parser.py`.
* Ensure `.gitignore` excludes virtual environments, build artifacts, and IDE files.

---

## Contribution

* Fork the repo and create a branch for your feature.
* Write **unit tests** for any new functionality.
* Submit a **pull request** with clear description and examples.

---

## License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## References

* [OAG MVT/MVA/DIV Message Types and Examples](https://www.oag.com/hubfs/Inbound-Services/OAG-MVT-MVA-DIV-Message-Types-and-Examples.pdf)
