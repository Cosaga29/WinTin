import re

# TINTIN Array manip
TINTIN_ARRAY_BETWEEN = re.compile(r"}{\d+}{")
TINTIN_ARRAY_BEGIN = re.compile(r"\d+}{")

# Player color matching. Depending on the terminals these might need adjusted
PLAYER_NAME_MATCH = re.compile(r"\x1b.*?\x1b\[.*?m(.*?)\x1b.*\x1b")

# Note that these are messages that might creep that
# normal punctionation might not pick up on
QUEUED_COMMAND_REGEX = re.compile(r".*?Queued command: .*?}{[0-9]+}")

# Hp: 2150
HP_MONITOR_REGEX = re.compile(r".*?Hp: .*?}{[0-9]+}")

# >
CURSOR_REGEX = re.compile(r".*?> {[0-9]+}")

# [Exp] Lyden Says: blah
CHAT_REGEX = re.compile(r".*?\[.*?\].*?{[0-9]+}")

CLIENT_ASYNC_TOKENS = [QUEUED_COMMAND_REGEX, HP_MONITOR_REGEX, CURSOR_REGEX, CHAT_REGEX]
