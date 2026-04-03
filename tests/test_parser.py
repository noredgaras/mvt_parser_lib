import json
import pytest
from mvt_parser import MVTParser, MVTMessage, MovementTime, Delay, PassengerInfo, FlightLeg, MVTParseError

# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)

# --- 1. Standard MVT Departure Message ---
def test_departure_message():
    raw = """
    MVT
    SD200/21.PMDFG.CDG
    AD1100/1115 EA1500 FRA
    DL72/0015
    PX112
    SI DEICING
    """
    msg = parse_msg(raw)
    assert msg.message_type == "MVT"
    assert msg.flight_number == "SD200"
    assert msg.airport_of_movement == "CDG"
    assert msg.actual_departure.primary == "1100"
    assert msg.actual_departure.secondary == "1115"
    assert msg.estimated_arrival == "1500"
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == ["72"]
    assert msg.delays[0].durations == ["0015"]
    assert msg.passenger_info.total == 112
    assert "DEICING" in msg.supplementary_info[0]

# --- 2. MVT Arrival Message ---
def test_arrival_message():
    raw = """
    MVT
    SD200/22.PMDFG.FRA
    AA1515/1520
    FLD22
    """
    msg = parse_msg(raw)
    assert msg.actual_arrival.primary == "1515"
    assert msg.actual_arrival.secondary == "1520"
    assert msg.flight_leg_date == "22"

# --- 3. Delay Line ---
def test_delay_message():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    ED221125
    DL72/0025
    """
    msg = parse_msg(raw)
    assert msg.estimated_departure == "221125"
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == ["72"]
    assert msg.delays[0].durations == ["0025"]

# --- 4. Next Info and Supplementary Info ---
def test_next_info_message():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    NI221150
    SI ENGINE TROUBLE
    """
    msg = parse_msg(raw)
    assert msg.next_info == "221150"
    assert "ENGINE TROUBLE" in msg.supplementary_info[0]

# --- 5. Delayed Takeoff ---
def test_delayed_takeoff():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    AD1115/1135
    SI DEICING
    """
    msg = parse_msg(raw)
    assert msg.actual_departure.primary == "1115"
    assert msg.actual_departure.secondary == "1135"
    assert "DEICING" in msg.supplementary_info[0]

# --- 6. Return from Airborne (FR) ---
def test_return_from_airborne():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    FR1200/1215 PX112
    SI ENGINE TROUBLE
    """
    msg = parse_msg(raw)
    assert msg.return_from_airborne == MovementTime(primary="1200", secondary="1215")
    assert msg.passenger_info.total == 112
    assert "ENGINE TROUBLE" in msg.supplementary_info[0]

# --- 7. Revised ETA and Onblock ---
def test_revised_eta():
    raw = """
    MVT
    SD200/22.PMDFG.FRA
    EA1515 EB1525
    SI RADAR FAILURE
    """
    msg = parse_msg(raw)
    assert msg.estimated_arrival == "1515"
    assert msg.estimated_onblock == "1525"
    assert "RADAR FAILURE" in msg.supplementary_info[0]

# --- 8. Arrival with Taxi Time and Passengers ---
def test_arrival_taxi_variance():
    raw = """
    MVT
    SD200/22.PMDFG.FRA
    AA1510 EB1520
    PX112/10
    """
    msg = parse_msg(raw)
    assert msg.actual_arrival.primary == "1510"
    assert msg.estimated_onblock == "1520"
    assert msg.passenger_info.total == 112
    assert msg.passenger_info.infants == 10

# --- 9. Diversion Message (DIV) ---
def test_diversion_message():
    raw = """
    DIV
    SD200/30.CVBNM.MAN
    EA1125 STN
    DR71 PX112
    SI BAD WEATHER
    """
    msg = parse_msg(raw)
    assert msg.message_type == "DIV"
    assert msg.flight_number == "SD200"
    assert msg.estimated_arrival == "1125"
    assert msg.diversion_reason == "71"
    assert msg.passenger_info.total == 112
    assert "BAD WEATHER" in msg.supplementary_info[0]

# --- 10. Crew Report, Takeoff Weight and Fuel ---
def test_flight_ops_tokens():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    CRT0930
    MAP1015
    TOF5000
    TOW70000
    ZFW60000
    """
    msg = parse_msg(raw)
    assert msg.crew_report_time == "0930"
    assert msg.movement_after_pushback == "1015"
    assert msg.takeoff_fuel == 5000
    assert msg.takeoff_weight == 70000
    assert msg.zero_fuel_weight == 60000

# --- 11. Unknown tokens go to unknown_lines; 3-letter codes go to destination_airport ---
def test_unknown_tokens():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    XY999 ABC
    """
    msg = parse_msg(raw)
    assert "XY999" in msg.unknown_lines
    assert msg.destination_airport == "ABC"

# --- 12. Invalid Header Throws Error ---
def test_invalid_message_raises():
    raw = """
    XXX
    SD200/22.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError):
        parser.parse(raw)

# --- 13. Empty Message Throws Error ---
def test_empty_message_raises():
    parser = MVTParser()
    with pytest.raises(MVTParseError):
        parser.parse("")

# --- 14. MVA Message Type ---
def test_mva_message():
    raw = """
    MVA
    BA200/15.XYZAB.LHR
    EA1430
    EB1445
    """
    msg = parse_msg(raw)
    assert msg.message_type == "MVA"
    assert msg.flight_number == "BA200"
    assert msg.estimated_arrival == "1430"
    assert msg.estimated_onblock == "1445"

# --- 15. Multi-leg Message ---
def test_multi_leg_message():
    raw = """
    MVT
    BA100/27.PPVMU.LHR
    AD1200/1210 EA1300 CDG
    AD1400/1415 EA1600 FRA
    """
    msg = parse_msg(raw)
    assert len(msg.legs) == 2
    assert msg.legs[0].actual_departure == MovementTime(primary="1200", secondary="1210")
    assert msg.legs[0].estimated_arrival == "1300"
    assert msg.legs[0].destination == "CDG"
    assert msg.legs[1].actual_departure == MovementTime(primary="1400", secondary="1415")
    assert msg.legs[1].estimated_arrival == "1600"
    assert msg.legs[1].destination == "FRA"
    # Primary fields capture first occurrence
    assert msg.actual_departure == MovementTime(primary="1200", secondary="1210")

# --- 16. Bad time format raises MVTParseError ---
def test_bad_time_format_raises():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    ED9999999
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format"):
        parser.parse(raw)

# --- 17. Bad numeric value raises MVTParseError ---
def test_bad_numeric_raises():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    TOFABC
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid takeoff fuel"):
        parser.parse(raw)

# --- 18. Invalid scheduled day raises MVTParseError ---
def test_invalid_day_raises():
    raw = """
    MVT
    SD200/00.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid scheduled day"):
        parser.parse(raw)

# --- 19. to_dict returns correct structure ---
def test_to_dict():
    raw = """
    MVT
    SD200/21.PMDFG.CDG
    AD1100/1115 EA1500 FRA
    PX112
    """
    msg = parse_msg(raw)
    d = msg.to_dict()
    assert d["flight_number"] == "SD200"
    assert d["actual_departure"] == {"primary": "1100", "secondary": "1115"}
    assert d["passenger_info"] == {"total": 112, "infants": None}

# --- 20. to_json returns valid JSON ---
def test_to_json():
    raw = """
    MVT
    SD200/21.PMDFG.CDG
    AD1100/1115
    """
    msg = parse_msg(raw)
    result = json.loads(msg.to_json())
    assert result["message_type"] == "MVT"
    assert result["flight_number"] == "SD200"
    assert result["actual_departure"] == {"primary": "1100", "secondary": "1115"}
