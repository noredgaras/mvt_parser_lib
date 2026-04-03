# mvt-parser

Python library for parsing IATA MVT flight movement messages.

## Install

```bash
pip install mvt-parser
```

## Quick start

```python
from mvt_parser import MVTParser

parser = MVTParser()
msg = parser.parse("""
MVT
BA100/27.PPVMU.LHR
AD1200/1210 EA1300 CDG
DL72/0015
PX145/12
SI DEICING
""")

print(msg.flight_number)          # BA100
print(msg.actual_departure)       # 1200/1210
print(msg.estimated_arrival)      # 1300
print(msg.delays[0].reason_codes) # ['72']
print(msg.passenger_info.total)   # 145
```

## Supported message types

| Type | Description |
|------|-------------|
| `MVT` | Movement — actual departure or arrival |
| `MVA` | Movement Advice — estimated time update |
| `DIV` | Diversion — flight redirected to another airport |

All three support optional `COR` (correction) and `REV` (revision) flags.

## Parsed fields

```python
msg.flight_number           # "BA100"
msg.scheduled_day           # "27"
msg.aircraft_registration   # "PPVMU"
msg.airport_of_movement     # "LHR"
msg.is_correction           # False
msg.is_revision             # False

msg.actual_departure        # MovementTime(primary="1200", secondary="1210")
msg.actual_arrival          # MovementTime(primary="1515", secondary=None)
msg.estimated_departure     # "1100"
msg.estimated_arrival       # "1300"
msg.estimated_onblock       # "1320"

msg.delays                  # [Delay(reason_codes=["72"], durations=["0015"])]
msg.passenger_info          # PassengerInfo(total=145, infants=12)
msg.destination_airport     # "CDG"
msg.reclearance             # "LHR"

msg.takeoff_fuel            # 6400
msg.takeoff_weight          # 70000
msg.zero_fuel_weight        # 60000

msg.diversion_reason        # "71"
msg.return_from_airborne    # MovementTime(primary="1400", secondary="1420")
msg.supplementary_info      # ["DEICING"]
msg.next_info               # "221150"
```

## Multi-leg flights

When a message contains multiple departure lines each line is captured as a `FlightLeg`:

```python
msg = parser.parse("""
MVT
BA100/27.PPVMU.LHR
AD1200/1210 EA1300 CDG
AD1400/1415 EA1600 FRA
""")

for leg in msg.legs:
    print(leg.actual_departure, "->", leg.destination)
# 1200/1210 -> CDG
# 1400/1415 -> FRA
```

## Export to dict / JSON

```python
msg.to_dict()  # plain Python dict
msg.to_json()  # pretty-printed JSON string
```

## Error handling

All parse failures raise `MVTParseError`:

```python
from mvt_parser import MVTParser, MVTParseError

try:
    msg = parser.parse(raw)
except MVTParseError as e:
    print(f"Invalid message: {e}")
```

## References

- [IATA MVT/MVA/DIV Message Types and Examples](https://www.oag.com/hubfs/Inbound-Services/OAG-MVT-MVA-DIV-Message-Types-and-Examples.pdf)

## License

MIT
