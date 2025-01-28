import re

# TINTIN Array manip
TINTIN_ARRAY_BETWEEN = re.compile(r"}{\d+}{")
TINTIN_ARRAY_BEGIN = re.compile(r"\d+}{")

# Player color matching. Depending on the terminals these might need adjusted
PLAYER_COLOR = re.compile(r"\x1b.*\x1b\[[0-9]+m(.*)\x1b.*\x1b")
PLAYER_COLOR_2 = re.compile(r"\x1b\[[0-9]+;[0-9]+m(.*)\x1b.*\x1b")

# Note that these are messages that might creep that 
# normal punctionation might not pick up on
QUEUED_COMMAND_REGEX = re.compile(r"}{[0-9]+}{Queued command: .*}{[0-9]+}{")
HP_MONITOR_REGEX = re.compile(r"}{Hp: .*}{[0-9]+}{")
CURSOR_REGEX = re.compile(r"}> {[0-9]+}{")
COMBINED_REGEX = re.compile(r"{[0-9]+}{Queued command: .*}{[0-9]+}{> }{[0-9]+}")

CLIENT_ASYNC_TOKENS = [QUEUED_COMMAND_REGEX, HP_MONITOR_REGEX, CURSOR_REGEX, COMBINED_REGEX]