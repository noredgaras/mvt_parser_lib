import re
from typing import List
from .models import MVTMessage, MovementTime, Delay, PassengerInfo
from .exceptions import MVTParseError

class MVTParser:
    HEADER = re.compile(r"^(MVT|MVA|DIV)(?:\s+(COR|REV))?$")
    FLIGHT = re.compile(r"^([A-Z0-9]+)/(\d{2})(?:\.([A-Z0-9]+))?\.(\w{3})$")

    def parse(self, raw: str) -> MVTMessage:
        lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip()]
        if not lines:
            raise MVTParseError("Empty message")

        msg, *rest = lines
        hm = self.HEADER.match(msg)
        if not hm:
            raise MVTParseError("Invalid header")
        mtype, flag = hm.groups()
        is_corr = flag == "COR"
        is_rev = flag == "REV"

        flight_line = rest.pop(0)
        fm = self.FLIGHT.match(flight_line)
        if not fm:
            raise MVTParseError("Invalid flight line")
        flight_no, sched_day, ac_reg, apt = fm.groups()

        m = MVTMessage(
            message_type=mtype,
            is_correction=is_corr,
            is_revision=is_rev,
            flight_number=flight_no,
            scheduled_day=sched_day,
            aircraft_registration=ac_reg,
            airport_of_movement=apt
        )

        for line in rest:
            self._parse_line(line, m)
        return m

    def _parse_line(self, line: str, m: MVTMessage):
        tokens = line.split()
        for token in tokens:
            if token.startswith("AD"):
                m.actual_departure = self._get_movement(token[2:])
            elif token.startswith("AA"):
                m.actual_arrival = self._get_movement(token[2:])
            elif token.startswith("ED"):
                m.estimated_departure = token[2:]
            elif token.startswith("EA"):
                m.estimated_arrival = token[2:]
            elif token.startswith("EB"):
                m.estimated_onblock = token[2:]
            elif token.startswith("DL"):
                m.delays.append(self._parse_delay(token[2:]))
            elif token.startswith("NI"):
                m.next_info = token[2:]
            elif token.startswith("PX"):
                m.passenger_info = self._parse_passenger(token[2:])
            elif token.startswith("RC"):
                m.reclearance = token[2:]
            elif token.startswith("FLD"):
                m.flight_leg_date = token[3:]
            elif token.startswith("CRT"):
                m.crew_report_time = token[3:]
            elif token.startswith("MAP"):
                m.movement_after_pushback = token[3:]
            elif token.startswith("TOF"):
                m.takeoff_fuel = int(token[3:])
            elif token.startswith("TOW"):
                m.takeoff_weight = int(token[3:])
            elif token.startswith("ZFW"):
                m.zero_fuel_weight = int(token[3:])
            else:
                m.unknown_lines.append(token)

    def _get_movement(self, t: str) -> MovementTime:
        parts = t.split("/")
        return MovementTime(primary=parts[0], secondary=parts[1] if len(parts) > 1 else None)

    def _parse_delay(self, val: str) -> Delay:
        parts = val.split("/")
        codes = [parts[0]] if len(parts) >= 1 else []
        durations = parts[1:] if len(parts) > 1 else []
        return Delay(reason_codes=codes, durations=durations)

    def _parse_passenger(self, val: str) -> PassengerInfo:
        parts = val.split("/")
        total = int(parts[0])
        infants = int(parts[1]) if len(parts) > 1 else None
        return PassengerInfo(total=total, infants=infants)
