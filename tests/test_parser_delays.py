import pytest

from mvt_parser import MVTParser


# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)


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