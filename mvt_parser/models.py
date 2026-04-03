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
    next_info: Optional[str] = None
    supplementary_info: List[str] = field(default_factory=list)

    # Passengers
    passenger_info: Optional[PassengerInfo] = None

    # Flight operations
    reclearance: Optional[str] = None
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

    # Unknown/unhandled lines
    unknown_lines: List[str] = field(default_factory=list)

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
            parts.append(f"  RC: {self.reclearance}")
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
        if self.diversion_reason:
            parts.append(f"  DR: {self.diversion_reason}")
        if self.return_from_airborne:
            parts.append(f"  FR: {self.return_from_airborne}")
        if self.next_info:
            parts.append(f"  NI: {self.next_info}")
        for si in self.supplementary_info:
            parts.append(f"  SI: {si}")
        if self.unknown_lines:
            parts.append(f"  Unknown: {self.unknown_lines}")
        return "\n".join(parts)
