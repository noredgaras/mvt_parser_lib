import pytest

from mvt_parser import MVTParser


# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)


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
    assert msg.legs[0].actual_departure.primary == "1200"
    assert msg.legs[0].actual_departure.secondary == "1210"
    assert msg.legs[0].estimated_arrival == "1300"
    assert msg.legs[0].destination == "CDG"
    assert msg.legs[1].actual_departure.primary == "1400"
    assert msg.legs[1].actual_departure.secondary == "1415"
    assert msg.legs[1].estimated_arrival == "1600"
    assert msg.legs[1].destination == "FRA"
    # Primary fields capture first occurrence
    assert msg.actual_departure.primary == "1200"
    assert msg.actual_departure.secondary == "1210"


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