import pytest

from mvt_parser import MVTParseError, MVTParser


# --- Helper ---
def parse_msg(raw):
    parser = MVTParser()
    return parser.parse(raw)


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