import re

QUEUED_COMMAND_TEXT = "Queued command:"
TINTIN_COMMAND_TEXT = ">"

TINTIN_ARRAY_BETWEEN = re.compile(r"}{\d+}{")
TINTIN_ARRAY_BEGIN = re.compile(r"\d+}{")
MDT_COMMAND_QUEUE = re.compile(r"Queued command: map door text ")
TINTIN_COMMAND = re.compile(r"> ")
PLAYER_COLOR = re.compile(r"\x1b\[.*m(.*)\x1b.*\x1b")
