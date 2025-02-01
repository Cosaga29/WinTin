import re
from enum import Enum
from typing import NamedTuple


class WeaponType(Enum):
    SHARP = 0
    PIERCE_STAB = 1
    SHARP_SLICE = 2


class DamageEntry(NamedTuple):
    matcher: re.Pattern
    damage: float


DIRKS = re.compile(r"jagged coral dirk")
FANGS = re.compile(r"sea serpent fang")
KATANA = re.compile(r"katana")


WEAPON_DAMAGE_TABLE: list[tuple[re.Pattern, WeaponType]] = [
    (DIRKS, WeaponType.SHARP),
    (FANGS, WeaponType.PIERCE_STAB),
    (KATANA, WeaponType.SHARP_SLICE),
]


DAMAGE_TABLE: list[list[DamageEntry]] = [
    # SHARP (Cosaga, Lyden)
    [
        DamageEntry(matcher=re.compile(r"(.*?) slashes at"), damage=0),
        DamageEntry(matcher=re.compile(r"(.*?) snicks"), damage=20),
        DamageEntry(matcher=re.compile(r"(.*?) scratches"), damage=60),
        DamageEntry(matcher=re.compile(r"(.*?) nicks"), damage=100),
        DamageEntry(matcher=re.compile(r"(.*?) cuts"), damage=140),
        DamageEntry(matcher=re.compile(r"(.*?) slices"), damage=180),
        DamageEntry(matcher=re.compile(r"(.*?) hacks"), damage=220),
        DamageEntry(matcher=re.compile(r"(.*?) chops up"), damage=500),
    ],
    # PIERCE_STAB (Micah, Masume sea serpent fangs)
    [
        DamageEntry(matcher=re.compile(r"(.*?) thrusts at"), damage=0),
        DamageEntry(matcher=re.compile(r"(.*?) barely stabs"), damage=20),
        DamageEntry(matcher=re.compile(r"(.*?) stabs"), damage=60),
        DamageEntry(matcher=re.compile(r"(.*?) messily stabs"), damage=100),
        DamageEntry(matcher=re.compile(r"(.*?) stabs .*? deeply"), damage=140),
        DamageEntry(matcher=re.compile(r"(.*?) perforate"), damage=180),
        DamageEntry(matcher=re.compile(r"(.*?) pierces"), damage=220),
        DamageEntry(matcher=re.compile(r"(.*?) stabs .*? right through"), damage=500),
    ],
    # SHARP_SLICE (Masume katana)
    [
        DamageEntry(matcher=re.compile(r"(.*?) slices at"), damage=0),
        DamageEntry(matcher=re.compile(r"(.*?) just manages to slice"), damage=20),
        DamageEntry(matcher=re.compile(r"(.*?) slices weapon across"), damage=60),
        DamageEntry(matcher=re.compile(r"(.*?) shreds"), damage=100),
        DamageEntry(matcher=re.compile(r"(.*?) slices"), damage=140),
        DamageEntry(matcher=re.compile(r"(.*?) takes a sliver off"), damage=180),
        DamageEntry(matcher=re.compile(r"(.*?) slices (.*?) deeply"), damage=220),
        DamageEntry(matcher=re.compile(r"(.*?) neatly fillets"), damage=500),
    ],
]
