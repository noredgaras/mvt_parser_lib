import pytest

from mvt_parser import MVTParser


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
    assert msg.return_from_airborne.primary == "1200"
    assert msg.return_from_airborne.secondary == "1215"
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