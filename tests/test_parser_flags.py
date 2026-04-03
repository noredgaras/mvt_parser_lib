import pytest

from mvt_parser import MVTParser


# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)


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