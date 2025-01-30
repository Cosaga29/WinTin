from enum import Enum
from dataclasses import dataclass

class WeaponType(Enum):
    SHARP = 0
    PIERCE_STAB = 1
    #SHARP_SLICE = 3
    #SHARP_CHOP = 4
    #SHARP = 0
    #SHARP_SLICE = 5

@dataclass
class DpsConfig:
    include: list[str]
    watch_path: str
    poll_rate: float
    weapon_map: dict[str, list[WeaponType]]
