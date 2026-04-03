import re
from typing import Optional

from .exceptions import MVTParseError
from .models import Delay, FlightLeg, MovementTime, MVTMessage, PassengerInfo

_TIME_RE = re.compile(r'^\d{4}$|^\d{6}$')
_IATA_RE = re.compile(r'^[A-Z]{3}$')


class MVTParser:
    HEADER = re.compile(r"^(MVT|MVA|DIV)(?:\s+(COR|REV))?$")
    FLIGHT = re.compile(r"^([A-Z0-9]+)/(\d{2})(?:\.([A-Z0-9]+))?\.([A-Z]{3})$")

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

        if not 1 <= int(sched_day) <= 31:
            raise MVTParseError(f"Invalid scheduled day: {sched_day!r}")

        msg = MVTMessage(
            message_type=mtype,
            is_correction=is_corr,
            is_revision=is_rev,
            flight_number=flight_no,
            scheduled_day=sched_day,
            aircraft_registration=ac_reg,
            airport_of_movement=apt
        )

        for line in rest:
            self._parse_line(line, msg)

        return msg

    def _parse_line(self, line: str, m: MVTMessage):
        if not self._parse_full_line(line, m):
            self._parse_tokens(line, m)

    def _parse_full_line(self, line: str, m: MVTMessage) -> bool:
        """Handle lines where the entire content belongs to one prefix. Returns True if handled."""
        if line.startswith("SI"):
            m.supplementary_info.append(line[2:].strip())
            return True

        if line.startswith("DR"):
            parts = line[2:].strip().split()
            m.diversion_reason = parts[0] if parts else None
            if len(parts) > 1 and parts[1].startswith("PX"):
                m.passenger_info = self._parse_passenger(parts[1][2:])
            return True

        if line.startswith("FR"):
            parts = line[2:].strip().split()
            m.return_from_airborne = self._get_movement(parts[0]) if parts else None
            if len(parts) > 1 and parts[1].startswith("PX"):
                m.passenger_info = self._parse_passenger(parts[1][2:])
            return True

        if line.startswith("RR"):
            parts = line[2:].strip().split()
            m.return_to_ramp = self._get_movement(parts[0]) if parts else None
            return True

        if line.startswith("PX"):
            m.passenger_info = self._parse_passenger(line[2:].strip())
            return True

        if line.startswith("DLA"):
            m.sub_delay_code = line[3:].strip()
            return True

        if line.startswith("DL"):
            m.delays.append(self._parse_delay(line[2:].strip()))
            return True

        if line.startswith("EDL"):
            m.extra_delay_info = line[3:].strip()
            return True

        if line.startswith("NI"):
            val = line[2:].strip()
            self._validate_time(val, "NI")
            m.next_info = val
            return True

        return False

    def _parse_tokens(self, line: str, m: MVTMessage):
        """Handle space-separated token lines, tracking context for IATA code disambiguation."""
        tokens = line.split()
        current_leg: Optional[FlightLeg] = None
        last_token_type: Optional[str] = None

        for token in tokens:
            if token.startswith("AD"):
                mt = self._get_movement(token[2:])
                if m.actual_departure is None:
                    m.actual_departure = mt
                current_leg = FlightLeg(actual_departure=mt)
                m.legs.append(current_leg)
                last_token_type = "AD"
            elif token.startswith("AA"):
                mt = self._get_movement(token[2:])
                if m.actual_arrival is None:
                    m.actual_arrival = mt
                if current_leg is None:
                    current_leg = FlightLeg(actual_arrival=mt)
                    m.legs.append(current_leg)
                else:
                    current_leg.actual_arrival = mt
                last_token_type = "AA"
            elif token.startswith("ED"):
                val = token[2:]
                self._validate_time(val, "ED")
                m.estimated_departure = val
                if current_leg:
                    current_leg.estimated_departure = val
                last_token_type = "ED"
            elif token.startswith("EA"):
                val = token[2:]
                self._validate_time(val, "EA")
                m.estimated_arrival = val
                if current_leg:
                    current_leg.estimated_arrival = val
                last_token_type = "EA"
            elif token.startswith("EO"):
                val = token[2:]
                self._validate_time(val, "EO")
                m.estimated_takeoff = val
                if current_leg:
                    current_leg.estimated_takeoff = val
                last_token_type = "EO"
            elif token.startswith("EB"):
                val = token[2:]
                self._validate_time(val, "EB")
                m.estimated_onblock = val
                if current_leg:
                    current_leg.estimated_onblock = val
                last_token_type = "EB"
            elif token.startswith("RC"):
                m.reclearance = token[2:]
                last_token_type = "RC"
            elif token.startswith("FLD"):
                val = token[3:]
                try:
                    day = int(val)
                except ValueError:
                    raise MVTParseError(f"Invalid flight leg date: {val!r}")
                if not 1 <= day <= 31:
                    raise MVTParseError(f"Invalid flight leg date: {val!r}")
                m.flight_leg_date = val
                last_token_type = "FLD"
            elif token.startswith("CRT"):
                val = token[3:]
                self._validate_time(val, "CRT")
                m.crew_report_time = val
                last_token_type = "CRT"
            elif token.startswith("MAP"):
                val = token[3:]
                self._validate_time(val, "MAP")
                m.movement_after_pushback = val
                last_token_type = "MAP"
            elif token.startswith("TOF"):
                try:
                    m.takeoff_fuel = int(token[3:])
                except ValueError:
                    raise MVTParseError(f"Invalid takeoff fuel value: {token[3:]!r}")
                last_token_type = "TOF"
            elif token.startswith("TOW"):
                try:
                    m.takeoff_weight = int(token[3:])
                except ValueError:
                    raise MVTParseError(f"Invalid takeoff weight value: {token[3:]!r}")
                last_token_type = "TOW"
            elif token.startswith("ZFW"):
                try:
                    m.zero_fuel_weight = int(token[3:])
                except ValueError:
                    raise MVTParseError(f"Invalid zero fuel weight value: {token[3:]!r}")
                last_token_type = "ZFW"
            elif _IATA_RE.match(token):
                if last_token_type == "RC":
                    m.reclearance_airport = token
                else:
                    m.destination_airport = token
                    if current_leg:
                        current_leg.destination = token
                last_token_type = "IATA"
            else:
                m.unknown_lines.append(token)
                last_token_type = None

    def _get_movement(self, t: str) -> MovementTime:
        parts = t.split("/")
        primary = parts[0]
        self._validate_time(primary, "movement time")
        secondary = parts[1] if len(parts) > 1 else None
        if secondary:
            self._validate_time(secondary, "movement time secondary")
        return MovementTime(primary=primary, secondary=secondary)

    def _validate_time(self, val: str, context: str) -> None:
        if not _TIME_RE.match(val):
            raise MVTParseError(f"Invalid time format in {context}: {val!r}")

    def _parse_delay(self, val: str) -> Delay:
        # Delay reason codes are 2-digit; durations are 4-digit HHMM
        parts = val.split("/")
        reason_codes = []
        durations = []
        for part in parts:
            if re.match(r'^\d{4}$', part):
                durations.append(part)
            else:
                reason_codes.append(part)
        return Delay(reason_codes=reason_codes, durations=durations)

    def _parse_passenger(self, val: str) -> PassengerInfo:
        parts = val.split("/")
        try:
            total = int(parts[0])
        except ValueError:
            raise MVTParseError(f"Invalid passenger count: {parts[0]!r}")
        infants = None
        if len(parts) > 1:
            try:
                infants = int(parts[1])
            except ValueError:
                raise MVTParseError(f"Invalid infant count: {parts[1]!r}")
        return PassengerInfo(total=total, infants=infants)
