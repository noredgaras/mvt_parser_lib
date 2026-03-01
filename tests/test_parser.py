from mvt_parser import MVTParser, MVTParseError

def test_basic_parse():
    raw_msg = """
    MVT
    BA100/27.PPVMU.LTN
    AD1200/1210 EA1300 CDG
    DL72/0015/0020
    PX145/12
    """
    parser = MVTParser()
    msg = parser.parse(raw_msg)
    assert msg.flight_number == "BA100"
    assert msg.actual_departure.primary == "1200"
    assert msg.passenger_info.total == 145
