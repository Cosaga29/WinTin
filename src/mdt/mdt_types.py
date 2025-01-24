import re
from typing import NamedTuple
from dataclasses import dataclass, field


class ConfigEntry(NamedTuple):
    pattern: re.Pattern | str
    terminal_color_code: str
    score: int


@dataclass
class RoomInfo:
    score: int = 0
    entities: list[str] = field(default_factory=list)
