from mvt_parser import MVTParser

raw_msg = """
MVT
BA100/27.PPVMU.LTN
AD1200/1210 EA1300 CDG
DL72/0015/0020
PX145/12
RC0945 LHR
FLD27
CRT0800
TOF6400
"""

parser = MVTParser()
msg = parser.parse(raw_msg)
print(msg)
