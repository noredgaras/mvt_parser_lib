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

        # Header
        header_line, *rest = lines
        hm = self.HEADER.match(header_line)
        if not hm:
            raise MVTParseError("Invalid header")
        mtype, flag = hm.groups()
        is_corr = flag == "COR"
        is_rev = flag == "REV"

        # Flight line
        if not rest:
            raise MVTParseError("Missing flight line")
        flight_line = rest.pop(0)
        fm = self.FLIGHT.match(flight_line)
        if not fm:
            raise MVTParseError("Invalid flight line")
        flight_no, sched_day, ac_reg, apt = fm.groups()

        msg = MVTMessage(
            message_type=mtype,
            is_correction=is_corr,
            is_revision=is_rev,
            flight_number=flight_no,
            scheduled_day=sched_day,
            aircraft_registration=ac_reg,
            airport_of_movement=apt
        )

        # Parse remaining lines
        for line in rest:
            self._parse_line(line, msg)

        return msg
    
    def _parse_line(self, line: str, m: MVTMessage):
        # Line-based tokens
        if line.startswith("SI"):
            m.supplementary_info.append(line[2:].strip())
            return

        if line.startswith("DR"):
            parts = line[2:].strip().split()
            m.diversion_reason = parts[0] if parts else None
            if len(parts) > 1 and parts[1].startswith("PX"):
                m.passenger_info = self._parse_passenger(parts[1][2:])
            return

        if line.startswith("FR"):
            parts = line[2:].strip().split()
            m.return_from_airborne = parts[0] if parts else None
            if len(parts) > 1 and parts[1].startswith("PX"):
                m.passenger_info = self._parse_passenger(parts[1][2:])
            return

        if line.startswith("PX"):
            m.passenger_info = self._parse_passenger(line[2:].strip())
            return

        if line.startswith("DL"):
            m.delays.append(self._parse_delay(line[2:].strip()))
            return

        if line.startswith("NI"):
            m.next_info = line[2:].strip()
            return

        # Remaining tokens split by space
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
        codes = [parts[0]] if parts else []
        durations = parts[1:] if len(parts) > 1 else []
        return Delay(reason_codes=codes, durations=durations)

    def _parse_passenger(self, val: str) -> PassengerInfo:
        parts = val.split("/")
        total = int(parts[0])
        infants = int(parts[1]) if len(parts) > 1 else None
        return PassengerInfo(total=total, infants=infants)