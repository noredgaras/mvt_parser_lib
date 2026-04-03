import json

import pytest

from mvt_parser import (
    MovementTime,
    MVTParseError,
    MVTParser,
)


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

# --- 21. COR flag parsing ---
def test_cor_flag():
    raw = """
    MVT COR
    SD200/21.PMDFG.CDG
    AD1100/1115
    """
    msg = parse_msg(raw)
    assert msg.message_type == "MVT"
    assert msg.is_correction is True
    assert msg.is_revision is False

# --- 22. REV flag parsing ---
def test_rev_flag():
    raw = """
    MVT REV
    SD200/21.PMDFG.CDG
    AD1100/1115
    """
    msg = parse_msg(raw)
    assert msg.message_type == "MVT"
    assert msg.is_correction is False
    assert msg.is_revision is True

# --- 23. MVA message with more fields ---
def test_mva_comprehensive():
    raw = """
    MVA
    BA200/15.XYZAB.LHR
    EA1430
    EB1445
    PX150/5
    DL93/0030
    SI MAINTENANCE DELAY
    """
    msg = parse_msg(raw)
    assert msg.message_type == "MVA"
    assert msg.flight_number == "BA200"
    assert msg.estimated_arrival == "1430"
    assert msg.estimated_onblock == "1445"
    assert msg.passenger_info.total == 150
    assert msg.passenger_info.infants == 5
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == ["93"]
    assert msg.delays[0].durations == ["0030"]
    assert "MAINTENANCE DELAY" in msg.supplementary_info[0]

# --- 24. DIV message with diversion details ---
def test_div_comprehensive():
    raw = """
    DIV
    SD200/30.CVBNM.MAN
    EA1125 STN
    DR71 PX112/3
    DL85/0045
    SI BAD WEATHER DIVERSION
    """
    msg = parse_msg(raw)
    assert msg.message_type == "DIV"
    assert msg.estimated_arrival == "1125"
    assert msg.destination_airport == "STN"
    assert msg.diversion_reason == "71"
    assert msg.passenger_info.total == 112
    assert msg.passenger_info.infants == 3
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == ["85"]
    assert msg.delays[0].durations == ["0045"]
    assert "BAD WEATHER DIVERSION" in msg.supplementary_info[0]

# --- 25. Multiple delays ---
def test_multiple_delays():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    DL72/0015 85/0030
    """
    msg = parse_msg(raw)
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == ["72", "0015 85"]
    assert msg.delays[0].durations == ["0030"]

# --- 26. Delay with only reason codes ---
def test_delay_only_reasons():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    DL72 85
    """
    msg = parse_msg(raw)
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == ["72 85"]
    assert msg.delays[0].durations == []

# --- 27. Delay with only durations ---
def test_delay_only_durations():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    DL0015/0030
    """
    msg = parse_msg(raw)
    assert len(msg.delays) == 1
    assert msg.delays[0].reason_codes == []
    assert msg.delays[0].durations == ["0015", "0030"]

# --- 28. Invalid passenger count ---
def test_invalid_passenger_count():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    PXABC
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid passenger count"):
        parser.parse(raw)

# --- 29. Invalid infant count ---
def test_invalid_infant_count():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    PX100/DEF
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid infant count"):
        parser.parse(raw)

# --- 30. Invalid takeoff fuel ---
def test_invalid_takeoff_fuel():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    TOFXYZ
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid takeoff fuel value"):
        parser.parse(raw)

# --- 31. Invalid takeoff weight ---
def test_invalid_takeoff_weight():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    TOWABC
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid takeoff weight value"):
        parser.parse(raw)

# --- 32. Invalid zero fuel weight ---
def test_invalid_zero_fuel_weight():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    ZFW123ABC
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid zero fuel weight value"):
        parser.parse(raw)

# --- 33. Invalid time format in AD ---
def test_invalid_ad_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    AD123/4567
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format in movement time"):
        parser.parse(raw)

# --- 34. Invalid time format in AA ---
def test_invalid_aa_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    AA99
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format in movement time"):
        parser.parse(raw)

# --- 35. Invalid time format in ED ---
def test_invalid_ed_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    ED12345
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format in ED"):
        parser.parse(raw)

# --- 36. Invalid time format in EA ---
def test_invalid_ea_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    EA999
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format in EA"):
        parser.parse(raw)

# --- 37. Invalid time format in EB ---
def test_invalid_eb_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    EB12
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format in EB"):
        parser.parse(raw)

# --- 38. Invalid time format in NI ---
def test_invalid_ni_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    NI1234567
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid time format in NI"):
        parser.parse(raw)

# --- 39. Invalid header with extra text ---
def test_invalid_header_extra():
    raw = """
    MVT EXTRA
    SD200/22.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid header"):
        parser.parse(raw)

# --- 40. Invalid flight line format ---
def test_invalid_flight_line():
    raw = """
    MVT
    SD200-22.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid flight line"):
        parser.parse(raw)

# --- 41. Flight line with invalid day ---
def test_flight_line_invalid_day():
    raw = """
    MVT
    SD200/32.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid scheduled day"):
        parser.parse(raw)

# --- 42. Flight line with day 00 ---
def test_flight_line_day_zero():
    raw = """
    MVT
    SD200/00.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid scheduled day"):
        parser.parse(raw)

# --- 43. Missing flight line ---
def test_missing_flight_line():
    raw = """
    MVT
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Missing flight line"):
        parser.parse(raw)

# --- 44. Multiple SI lines ---
def test_multiple_si_lines():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    SI FIRST INFO
    SI SECOND INFO
    SI THIRD INFO
    """
    msg = parse_msg(raw)
    assert len(msg.supplementary_info) == 3
    assert "FIRST INFO" in msg.supplementary_info[0]
    assert "SECOND INFO" in msg.supplementary_info[1]
    assert "THIRD INFO" in msg.supplementary_info[2]

# --- 45. RC reclearance ---
def test_reclearance():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    RC1234
    """
    msg = parse_msg(raw)
    assert msg.reclearance == "1234"

# --- 46. FLD flight leg date ---
def test_flight_leg_date():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    FLD25
    """
    msg = parse_msg(raw)
    assert msg.flight_leg_date == "25"

# --- 47. CRT crew report time ---
def test_crew_report_time():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    CRT0800
    """
    msg = parse_msg(raw)
    assert msg.crew_report_time == "0800"

# --- 48. MAP movement after pushback ---
def test_movement_after_pushback():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    MAP1030
    """
    msg = parse_msg(raw)
    assert msg.movement_after_pushback == "1030"

# --- 49. TOF takeoff fuel ---
def test_takeoff_fuel():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    TOF15000
    """
    msg = parse_msg(raw)
    assert msg.takeoff_fuel == 15000

# --- 50. TOW takeoff weight ---
def test_takeoff_weight():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    TOW80000
    """
    msg = parse_msg(raw)
    assert msg.takeoff_weight == 80000

# --- 51. ZFW zero fuel weight ---
def test_zero_fuel_weight():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    ZFW65000
    """
    msg = parse_msg(raw)
    assert msg.zero_fuel_weight == 65000

# --- 52. Multiple unknown tokens ---
def test_multiple_unknown_tokens():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    XYZ123 ABC DEF
    """
    msg = parse_msg(raw)
    assert "XYZ123" in msg.unknown_lines
    assert msg.destination_airport == "DEF"  # Last IATA code wins

# --- 53. Movement time without secondary ---
def test_movement_time_no_secondary():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    AD1200
    """
    msg = parse_msg(raw)
    assert msg.actual_departure.primary == "1200"
    assert msg.actual_departure.secondary is None

# --- 54. Complex multi-leg message ---
def test_complex_multi_leg():
    raw = """
    MVT
    BA100/27.PPVMU.LHR
    AD1200/1210 EA1300 CDG
    PX50
    AD1400/1415 EA1600 FRA
    PX75/2
    DL72/0020
    """
    msg = parse_msg(raw)
    assert len(msg.legs) == 2
    assert msg.legs[0].actual_departure.primary == "1200"
    assert msg.legs[0].estimated_arrival == "1300"
    assert msg.legs[0].destination == "CDG"
    assert msg.legs[1].actual_departure.primary == "1400"
    assert msg.legs[1].estimated_arrival == "1600"
    assert msg.legs[1].destination == "FRA"
    # Primary fields from first leg
    assert msg.actual_departure.primary == "1200"
    assert msg.estimated_arrival == "1600"  # Last EA wins
    assert msg.destination_airport == "FRA"  # Last destination wins
    # Passenger info from last PX
    assert msg.passenger_info.total == 75
    assert msg.passenger_info.infants == 2

# --- 55. DIV with FR return from airborne ---
def test_div_with_fr():
    raw = """
    DIV
    SD200/30.CVBNM.MAN
    FR1400/1420 PX85
    DR71
    """
    msg = parse_msg(raw)
    assert msg.message_type == "DIV"
    assert msg.return_from_airborne.primary == "1400"
    assert msg.return_from_airborne.secondary == "1420"
    assert msg.passenger_info.total == 85
    assert msg.diversion_reason == "71"

# --- 56. MVA with AA actual arrival ---
def test_mva_with_aa():
    raw = """
    MVA
    BA200/15.XYZAB.LHR
    AA1435/1450
    EB1500
    """
    msg = parse_msg(raw)
    assert msg.message_type == "MVA"
    assert msg.actual_arrival.primary == "1435"
    assert msg.actual_arrival.secondary == "1450"
    assert msg.estimated_onblock == "1500"

# --- 57. Invalid message type ---
def test_invalid_message_type():
    raw = """
    XYZ
    SD200/22.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid header"):
        parser.parse(raw)

# --- 58. Header with invalid flag ---
def test_invalid_flag():
    raw = """
    MVT XYZ
    SD200/22.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid header"):
        parser.parse(raw)

# --- 59. Flight line with invalid airport code ---
def test_invalid_airport_code():
    raw = """
    MVT
    SD200/22.PMDFG.123
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid flight line"):
        parser.parse(raw)

# --- 60. Flight line with invalid flight number ---
def test_invalid_flight_number():
    raw = """
    MVT
    SD-200/22.PMDFG.CDG
    """
    parser = MVTParser()
    with pytest.raises(MVTParseError, match="Invalid flight line"):
        parser.parse(raw)

# --- Round-trip tests (parse → to_mvt → parse) ---

def roundtrip(raw):
    parser = MVTParser()
    msg = parser.parse(raw)
    return parser.parse(msg.to_mvt())

def test_roundtrip_departure():
    raw = """
    MVT
    SD200/21.PMDFG.CDG
    AD1100/1115 EA1500 FRA
    DL72/0015
    PX112/3
    SI DEICING
    """
    original = parse_msg(raw)
    rt = roundtrip(raw)
    assert rt.flight_number == original.flight_number
    assert rt.actual_departure == original.actual_departure
    assert rt.estimated_arrival == original.estimated_arrival
    assert rt.delays[0].reason_codes == original.delays[0].reason_codes
    assert rt.passenger_info.total == original.passenger_info.total
    assert rt.supplementary_info == original.supplementary_info

def test_roundtrip_arrival():
    raw = """
    MVT
    SD200/22.PMDFG.FRA
    AA1515/1520
    FLD22
    """
    original = parse_msg(raw)
    rt = roundtrip(raw)
    assert rt.actual_arrival == original.actual_arrival
    assert rt.flight_leg_date == original.flight_leg_date

def test_roundtrip_diversion():
    raw = """
    DIV
    SD200/30.CVBNM.MAN
    EA1125 STN
    DR71 PX112/3
    SI BAD WEATHER
    """
    original = parse_msg(raw)
    rt = roundtrip(raw)
    assert rt.message_type == "DIV"
    assert rt.estimated_arrival == original.estimated_arrival
    assert rt.diversion_reason == original.diversion_reason
    assert rt.passenger_info.total == original.passenger_info.total

def test_roundtrip_multi_leg():
    raw = """
    MVT
    BA100/27.PPVMU.LHR
    AD1200/1210 EA1300 CDG
    AD1400/1415 EA1600 FRA
    """
    original = parse_msg(raw)
    rt = roundtrip(raw)
    assert len(rt.legs) == len(original.legs)
    assert rt.legs[0].actual_departure == original.legs[0].actual_departure
    assert rt.legs[0].destination == original.legs[0].destination
    assert rt.legs[1].actual_departure == original.legs[1].actual_departure
    assert rt.legs[1].destination == original.legs[1].destination

def test_roundtrip_flight_ops():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    CRT0930
    TOF5000
    TOW70000
    ZFW60000
    """
    original = parse_msg(raw)
    rt = roundtrip(raw)
    assert rt.crew_report_time == original.crew_report_time
    assert rt.takeoff_fuel == original.takeoff_fuel
    assert rt.takeoff_weight == original.takeoff_weight
    assert rt.zero_fuel_weight == original.zero_fuel_weight

def test_roundtrip_cor_flag():
    raw = """
    MVT COR
    SD200/21.PMDFG.CDG
    AD1100/1115
    """
    original = parse_msg(raw)
    rt = roundtrip(raw)
    assert rt.is_correction is True
    assert rt.actual_departure == original.actual_departure

def test_to_mvt_output():
    """Verify the raw MVT string format is correct."""
    parser = MVTParser()
    msg = parser.parse("""
    MVT
    BA100/27.PPVMU.LHR
    AD1200/1210 EA1300 CDG
    DL72/0015
    PX145/12
    SI DEICING
    """)
    mvt = msg.to_mvt()
    assert mvt.startswith("MVT")
    assert "BA100/27.PPVMU.LHR" in mvt
    assert "AD1200/1210" in mvt
    assert "EA1300" in mvt
    assert "DL72/0015" in mvt
    assert "PX145/12" in mvt
    assert "SI DEICING" in mvt

# --- reclearance_airport disambiguation ---

def test_reclearance_with_airport():
    raw = """
    MVT
    BA100/27.PPVMU.LHR
    AD1200/1210 EA1300 CDG
    RC0945 LHR
    """
    msg = parse_msg(raw)
    assert msg.reclearance == "0945"
    assert msg.reclearance_airport == "LHR"
    # destination_airport comes from EA context, not RC
    assert msg.destination_airport == "CDG"

def test_reclearance_without_airport():
    raw = """
    MVT
    SD200/22.PMDFG.CDG
    RC1234
    """
    msg = parse_msg(raw)
    assert msg.reclearance == "1234"
    assert msg.reclearance_airport is None

def test_roundtrip_reclearance_with_airport():
    raw = """
    MVT
    BA100/27.PPVMU.LHR
    AD1200/1210 EA1300 CDG
    RC0945 LHR
    """
    original = parse_msg(raw)
    rt = MVTParser().parse(original.to_mvt())
    assert rt.reclearance == original.reclearance
    assert rt.reclearance_airport == original.reclearance_airport
    assert rt.destination_airport == original.destination_airport
