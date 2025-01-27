import re

TINTIN_ARRAY_BETWEEN = re.compile(r"}{\d+}{")
TINTIN_ARRAY_BEGIN = re.compile(r"\d+}{")
MDT_COMMAND_QUEUE = re.compile(r"Queued command: map door text ")
PLAYER_COLOR = re.compile(r"\x1b\[.*\d+m(.*)\x1b.*\x1b")