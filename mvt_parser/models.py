import json
from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class Delay:
    reason_codes: List[str]
    durations: List[str]


@dataclass
class PassengerInfo:
    total: int
    infants: Optional[int] = None


@dataclass
class MovementTime:
    primary: str
    secondary: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.primary}/{self.secondary}" if self.secondary else self.primary


@dataclass
class FlightLeg:
    actual_departure: Optional[MovementTime] = None
    actual_arrival: Optional[MovementTime] = None
    estimated_departure: Optional[str] = None
    estimated_arrival: Optional[str] = None
    estimated_onblock: Optional[str] = None
    estimated_takeoff: Optional[str] = None
    destination: Optional[str] = None


@dataclass
class MVTMessage:
    # Header
    message_type: str
    is_correction: bool = False
    is_revision: bool = False

    # Flight info
    flight_number: str = ""
    scheduled_day: str = ""
    aircraft_registration: Optional[str] = None
    airport_of_movement: Optional[str] = None

    # Times
    actual_departure: Optional[MovementTime] = None
    actual_arrival: Optional[MovementTime] = None
    estimated_departure: Optional[str] = None
    estimated_arrival: Optional[str] = None
    estimated_onblock: Optional[str] = None

    # Flight legs (populated for multi-leg messages; first leg also sets primary time fields)
    legs: List[FlightLeg] = field(default_factory=list)

    # Delays & supplementary
    delays: List[Delay] = field(default_factory=list)
    sub_delay_code: Optional[str] = None
    extra_delay_info: Optional[str] = None
    next_info: Optional[str] = None
    supplementary_info: List[str] = field(default_factory=list)

    # Passengers
    passenger_info: Optional[PassengerInfo] = None

    # Flight operations
    reclearance: Optional[str] = None
    reclearance_airport: Optional[str] = None
    destination_airport: Optional[str] = None
    flight_leg_date: Optional[str] = None
    crew_report_time: Optional[str] = None
    movement_after_pushback: Optional[str] = None
    takeoff_fuel: Optional[int] = None
    takeoff_weight: Optional[int] = None
    zero_fuel_weight: Optional[int] = None

    # Special cases
    diversion_reason: Optional[str] = None
    return_from_airborne: Optional[MovementTime] = None
    return_to_ramp: Optional[MovementTime] = None
    estimated_takeoff: Optional[str] = None

    # Unknown/unhandled lines
    unknown_lines: List[str] = field(default_factory=list)

    def to_mvt(self) -> str:
        """Serialize back to MVT wire format. The result is parseable by MVTParser."""
        lines = []

        # Header
        flag = " COR" if self.is_correction else (" REV" if self.is_revision else "")
        lines.append(f"{self.message_type}{flag}")

        # Flight line
        flight = f"{self.flight_number}/{self.scheduled_day}"
        if self.aircraft_registration:
            flight += f".{self.aircraft_registration}"
        flight += f".{self.airport_of_movement}"
        lines.append(flight)

        # Movement lines — use legs if populated, otherwise primary fields
        if self.legs:
            for leg in self.legs:
                tokens = []
                if leg.actual_departure:
                    tokens.append(f"AD{leg.actual_departure}")
                if leg.actual_arrival:
                    tokens.append(f"AA{leg.actual_arrival}")
                if leg.estimated_departure:
                    tokens.append(f"ED{leg.estimated_departure}")
                if leg.estimated_arrival:
                    tokens.append(f"EA{leg.estimated_arrival}")
                if leg.estimated_onblock:
                    tokens.append(f"EB{leg.estimated_onblock}")
                if leg.estimated_takeoff:
                    tokens.append(f"EO{leg.estimated_takeoff}")
                if leg.destination:
                    tokens.append(leg.destination)
                if tokens:
                    lines.append(" ".join(tokens))
        else:
            tokens = []
            if self.actual_departure:
                tokens.append(f"AD{self.actual_departure}")
            if self.actual_arrival:
                tokens.append(f"AA{self.actual_arrival}")
            if self.estimated_departure:
                tokens.append(f"ED{self.estimated_departure}")
            if self.estimated_arrival:
                tokens.append(f"EA{self.estimated_arrival}")
                if self.destination_airport:
                    tokens.append(self.destination_airport)
            if tokens:
                lines.append(" ".join(tokens))

        if self.estimated_onblock:
            lines.append(f"EB{self.estimated_onblock}")
        if self.estimated_takeoff:
            lines.append(f"EO{self.estimated_takeoff}")

        # Delays
        for delay in self.delays:
            parts = delay.reason_codes + delay.durations
            lines.append(f"DL{'/'.join(parts)}")
        if self.sub_delay_code:
            lines.append(f"DLA{self.sub_delay_code}")
        if self.extra_delay_info:
            lines.append(f"EDL{self.extra_delay_info}")

        # RR — return to ramp
        if self.return_to_ramp:
            lines.append(f"RR{self.return_to_ramp}")

        # FR — passenger info attached when no diversion reason
        if self.return_from_airborne:
            line = f"FR{self.return_from_airborne}"
            if self.passenger_info and not self.diversion_reason:
                line += f" PX{self.passenger_info.total}"
                if self.passenger_info.infants is not None:
                    line += f"/{self.passenger_info.infants}"
            lines.append(line)

        # DR — passenger info attached on same line
        if self.diversion_reason:
            line = f"DR{self.diversion_reason}"
            if self.passenger_info:
                line += f" PX{self.passenger_info.total}"
                if self.passenger_info.infants is not None:
                    line += f"/{self.passenger_info.infants}"
            lines.append(line)
        elif self.passenger_info and not self.return_from_airborne:
            pax = f"PX{self.passenger_info.total}"
            if self.passenger_info.infants is not None:
                pax += f"/{self.passenger_info.infants}"
            lines.append(pax)

        if self.next_info:
            lines.append(f"NI{self.next_info}")
        if self.reclearance:
            rc = f"RC{self.reclearance}"
            if self.reclearance_airport:
                rc += f" {self.reclearance_airport}"
            lines.append(rc)
        if self.flight_leg_date:
            lines.append(f"FLD{self.flight_leg_date}")
        if self.crew_report_time:
            lines.append(f"CRT{self.crew_report_time}")
        if self.movement_after_pushback:
            lines.append(f"MAP{self.movement_after_pushback}")
        if self.takeoff_fuel is not None:
            lines.append(f"TOF{self.takeoff_fuel}")
        if self.takeoff_weight is not None:
            lines.append(f"TOW{self.takeoff_weight}")
        if self.zero_fuel_weight is not None:
            lines.append(f"ZFW{self.zero_fuel_weight}")
        for si in self.supplementary_info:
            lines.append(f"SI {si}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self) -> str:
        flag = " COR" if self.is_correction else (" REV" if self.is_revision else "")
        header = f"[{self.message_type}{flag}] {self.flight_number}/{self.scheduled_day}"
        if self.aircraft_registration:
            header += f".{self.aircraft_registration}"
        if self.airport_of_movement:
            header += f".{self.airport_of_movement}"
        parts = [header]
        if self.legs:
            for i, leg in enumerate(self.legs, 1):
                leg_parts = []
                if leg.actual_departure:
                    leg_parts.append(f"AD:{leg.actual_departure}")
                if leg.actual_arrival:
                    leg_parts.append(f"AA:{leg.actual_arrival}")
                if leg.estimated_departure:
                    leg_parts.append(f"ED:{leg.estimated_departure}")
                if leg.estimated_arrival:
                    leg_parts.append(f"EA:{leg.estimated_arrival}")
                if leg.destination:
                    leg_parts.append(f"→{leg.destination}")
                if leg_parts:
                    parts.append(f"  Leg {i}: {' '.join(leg_parts)}")
        else:
            if self.actual_departure:
                parts.append(f"  AD: {self.actual_departure}")
            if self.actual_arrival:
                parts.append(f"  AA: {self.actual_arrival}")
            if self.estimated_departure:
                parts.append(f"  ED: {self.estimated_departure}")
            if self.estimated_arrival:
                parts.append(f"  EA: {self.estimated_arrival}")
        if self.estimated_onblock:
            parts.append(f"  EB: {self.estimated_onblock}")
        if self.destination_airport and not self.legs:
            parts.append(f"  Destination: {self.destination_airport}")
        for d in self.delays:
            parts.append(f"  DL: codes={d.reason_codes} durations={d.durations}")
        if self.passenger_info:
            pax = str(self.passenger_info.total)
            if self.passenger_info.infants is not None:
                pax += f"/{self.passenger_info.infants} infants"
            parts.append(f"  PX: {pax}")
        if self.reclearance:
            rc = f"  RC: {self.reclearance}"
            if self.reclearance_airport:
                rc += f" {self.reclearance_airport}"
            parts.append(rc)
        if self.flight_leg_date:
            parts.append(f"  FLD: {self.flight_leg_date}")
        if self.crew_report_time:
            parts.append(f"  CRT: {self.crew_report_time}")
        if self.movement_after_pushback:
            parts.append(f"  MAP: {self.movement_after_pushback}")
        if self.takeoff_fuel is not None:
            parts.append(f"  TOF: {self.takeoff_fuel}")
        if self.takeoff_weight is not None:
            parts.append(f"  TOW: {self.takeoff_weight}")
        if self.zero_fuel_weight is not None:
            parts.append(f"  ZFW: {self.zero_fuel_weight}")
        if self.estimated_takeoff:
            parts.append(f"  EO: {self.estimated_takeoff}")
        if self.diversion_reason:
            parts.append(f"  DR: {self.diversion_reason}")
        if self.return_from_airborne:
            parts.append(f"  FR: {self.return_from_airborne}")
        if self.return_to_ramp:
            parts.append(f"  RR: {self.return_to_ramp}")
        if self.sub_delay_code:
            parts.append(f"  DLA: {self.sub_delay_code}")
        if self.extra_delay_info:
            parts.append(f"  EDL: {self.extra_delay_info}")
        if self.next_info:
            parts.append(f"  NI: {self.next_info}")
        for si in self.supplementary_info:
            parts.append(f"  SI: {si}")
        if self.unknown_lines:
            parts.append(f"  Unknown: {self.unknown_lines}")
        return "\n".join(parts)
