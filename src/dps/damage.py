import re
from typing import NamedTuple


class DamageEntry(NamedTuple):
    matcher: re.Pattern
    damage: float


DAMAGE_TABLE: list[list[DamageEntry]] = [
    # Only sharp for now
    [
        DamageEntry(matcher=re.compile(r"(.*?) slashes at"), damage=0),
        DamageEntry(matcher=re.compile(r"(.*?) snicks"), damage=20),
        DamageEntry(matcher=re.compile(r"(.*?) scratches"), damage=60),
        DamageEntry(matcher=re.compile(r"(.*?) nicks"), damage=100),
        DamageEntry(matcher=re.compile(r"(.*?) cuts"), damage=140),
        DamageEntry(matcher=re.compile(r"(.*?) slices"), damage=180),
        DamageEntry(matcher=re.compile(r"(.*?) hacks"), damage=220),
        DamageEntry(matcher=re.compile(r"(.*?) chops up"), damage=5000),
    ],
    [
        DamageEntry(matcher=re.compile(r"(.*?) thrusts at"), damage=0),
        DamageEntry(matcher=re.compile(r"(.*?) barely stabs"), damage=20),
        DamageEntry(matcher=re.compile(r"(.*?) stabs"), damage=60),
        DamageEntry(matcher=re.compile(r"(.*?) messily stabs"), damage=100),
        DamageEntry(matcher=re.compile(r"(.*?) stabs .*? deeply"), damage=140),
        DamageEntry(matcher=re.compile(r"(.*?) perforate"), damage=180),
        DamageEntry(matcher=re.compile(r"(.*?) pierces"), damage=220),
        DamageEntry(matcher=re.compile(r"(.*?) stabs .*? right through"), damage=5000),
    ]
]