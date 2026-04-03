# mvt-parser

Python library for parsing IATA MVT flight movement messages.

## What is MVT?

MVT (Movement), MVA (Movement Advice), and DIV (Diversion) are standardised plain-text telegrams exchanged between airlines, airports, and handling agents to communicate real-time flight events.

They are used to:
- Control punctual and regular operation of all flights
- Form the basis for aircraft and crew rotation planning
- Alert operations control centres to diversions and unplanned routing changes

A typical MVT message looks like this:

```
MVT
BA100/27.PPVMU.LHR
AD1200/1210 EA1300 CDG
DL72/0015
PX145/12
SI DEICING
```

Every message has the same structure:
1. **Header line** — message type (`MVT`, `MVA`, or `DIV`) with optional `COR` (correction) or `REV` (revision) flag
2. **Flight line** — flight number, scheduled day, aircraft registration, and airport of movement
3. **Body lines** — one or more lines carrying movement data using two- or three-letter tokens

### Tokens

| Token | Meaning | Example |
|-------|---------|---------|
| `AD` | Actual departure (off-block / airborne) | `AD1200/1210` |
| `AA` | Actual arrival (touchdown / on-block) | `AA1515/1520` |
| `EA` | Estimated arrival (touchdown) + airport | `EA1300 CDG` |
| `ED` | Estimated departure | `ED041630` |
| `EB` | Estimated on-block time | `EB1320` |
| `DL` | Delay — reason code(s) and duration(s) | `DL72/0015` |
| `PX` | Passengers on board / infants | `PX145/12` |
| `RC` | Reclearance time and airport | `RC1200 LTN` |
| `DR` | Diversion reason code | `DR71` |
| `FR` | Forced return from airborne | `FR1215/1235` |
| `NI` | Next information time (indefinite delay) | `NI052215` |
| `FLD` | Flight leg date | `FLD16` |
| `CRT` | Crew report time | `CRT1530` |
| `MAP` | Movement after pushback | `MAP1015` |
| `TOF` | Take-off fuel | `TOF6400` |
| `TOW` | Take-off weight | `TOW63452` |
| `ZFW` | Zero fuel weight | `ZFW132500` |
| `SI` | Supplementary free-text information | `SI DEICING` |

All times are UTC in `HHMM` (4-digit) or `DDHHMM` (6-digit) format.

---

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
msg.reclearance             # "0945"
msg.reclearance_airport     # "LHR"

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

## Serialize back to MVT

`to_mvt()` reconstructs the original wire format from parsed data — useful for forwarding or storing messages:

```python
msg = parser.parse(raw)

# modify a field
msg.estimated_arrival = "1400"

# serialize back
print(msg.to_mvt())
```

Output:
```
MVT
BA100/27.PPVMU.LHR
AD1200/1210 EA1400 CDG
DL72/0015
PX145/12
SI DEICING
```

The result is always valid and parseable back by `MVTParser`.

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
