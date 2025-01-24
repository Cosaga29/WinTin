import re
import os
import json

from maps import COLOR_MAP
from mdt_types import ConfigEntry

MDT_PARSE_DIR = os.path.abspath(os.path.dirname(__file__))


def build_match_config(config: dict) -> list[ConfigEntry]:
    match_config_list: list[ConfigEntry] = []
    custom_matches = config["custom_matches"]

    # Match entry: [pattern or string, color_string, score, is_regex_pattern]
    for match_entry in custom_matches:
        if len(match_entry) == 1:
            # Because someone thought it was a good idea to use an array of size 1 as a comment.
            # Seriously WTF is this?
            continue

        should_compile = match_entry[3]
        if should_compile:
            pattern = re.compile(match_entry[0])
        else:
            pattern = match_entry[0]

        # Reset the color by default
        terminal_color_code = COLOR_MAP["reset"]

        # Check if we have a valid color entry for this match
        if match_entry[1] != "" and match_entry[1] in COLOR_MAP:
            terminal_color_code = COLOR_MAP[match_entry[1]]

        match_config_list.append(
            ConfigEntry(pattern, terminal_color_code, match_entry[2])
        )

    return match_config_list


# Load the JSON configuration file
with open(os.path.join(MDT_PARSE_DIR, "config.json"), "r") as config_file:
    CONFIG = json.load(config_file)
    USER_MATCHES = build_match_config(CONFIG)


DEFAULT_NPC_VALUE = CONFIG["default_npc_value"]
BONUS_PLAYER_VALUE = CONFIG["bonus_player_value"]
MIN_ROOM_VALUE = CONFIG["minimum_room_value"]
SHOW_HIDDEN_ROOM_COUNT = CONFIG["show_hidden_room_count"]
