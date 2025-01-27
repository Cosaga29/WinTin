import re
from enum import Enum
from typing import NamedTuple
from dataclasses import dataclass, field


class ConfigEntry(NamedTuple):
    pattern: re.Pattern | str
    terminal_color_code: str
    curses_color_code: int
    score: int


@dataclass
class EntityInfo:
    count: int = 0
    description: str = ""
    curse_color_code: int = 1
    score: int = 0


@dataclass
class RoomInfo:
    score: int = 0
    entities: list[EntityInfo] = field(default_factory=list)


IGNORE_TOKENS = (
    "exit",
    "doors ",
    "a door ",
    "exits ",
    "an exit ",
    "a hard to see through exit ",
    "the limit of your",
)


NUMBER_MAP = {
    "a": 1,
    "a ": 1,
    "an": 1,
    "the": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "twenty-one": 21,
    "twenty-two": 22,
    "twenty-three": 23,
    "twenty-four": 24,
    "twenty-five": 25,
    "twenty-six": 26,
    "twenty-seven": 27,
    "twenty-eight": 28,
    "twenty-nine": 29,
    "thirty": 30,
}

DIRECTION_MAP = {
    "north": "n",
    "northeast": "ne",
    "east": "e",
    "southeast": "se",
    "south": "s",
    "southwest": "sw",
    "west": "w",
    "northwest": "nw",
    "n": "n",
    "ne": "ne",
    "e": "e",
    "se": "se",
    "s": "s",
    "sw": "sw",
    "w": "w",
    "nw": "nw",
}