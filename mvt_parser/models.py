from dataclasses import dataclass, field
from typing import Optional, List

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

    # Delays & supplementary
    delays: List[Delay] = field(default_factory=list)
    next_info: Optional[str] = None
    supplementary_info: List[str] = field(default_factory=list)

    # Passengers
    passenger_info: Optional[PassengerInfo] = None

    # Flight operations
    reclearance: Optional[str] = None
    flight_leg_date: Optional[str] = None
    crew_report_time: Optional[str] = None
    movement_after_pushback: Optional[str] = None
    takeoff_fuel: Optional[int] = None
    takeoff_weight: Optional[int] = None
    zero_fuel_weight: Optional[int] = None

    # Special cases
    diversion_reason: Optional[str] = None
    return_from_airborne: Optional[str] = None

    # Unknown/unhandled lines
    unknown_lines: List[str] = field(default_factory=list)