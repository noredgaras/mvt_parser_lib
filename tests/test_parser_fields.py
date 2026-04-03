import pytest

from mvt_parser import MVTParser


# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)


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