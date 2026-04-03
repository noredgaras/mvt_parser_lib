import json

import pytest

from mvt_parser import MVTParser


# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)


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