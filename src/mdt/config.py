import re
import os
import json
import curses
from enum import Enum

from mdt.definitions import ConfigEntry


class MdtColors(Enum):
    WHITE_BLACK = 1
    CYAN_BLACK = 2
    RED_BLACK = 3
    YELLOW_BLACK = 4


CONFIG_COLOR_MAP = {
    "reset": MdtColors.WHITE_BLACK,
    "cyan": MdtColors.CYAN_BLACK,
    "red": MdtColors.RED_BLACK,
    "orange": MdtColors.YELLOW_BLACK,
}

BASH_COLOR_MAP = {
    # http://terminal-color-builder.mudasobwa.ru/
    MdtColors.YELLOW_BLACK: "\033[01;38;05;214m",
    MdtColors.RED_BLACK: "\033[01;38;05;196m",
    MdtColors.CYAN_BLACK: "\033[01;38;05;37m",
    MdtColors.WHITE_BLACK: "\033[00;39;49m",
}

CURSES_COLOR_PAIR_MAP = {
    MdtColors.WHITE_BLACK: (curses.COLOR_WHITE, curses.COLOR_BLACK),
    MdtColors.CYAN_BLACK: (curses.COLOR_CYAN, curses.COLOR_BLACK),
    MdtColors.RED_BLACK: (curses.COLOR_RED, curses.COLOR_BLACK),
    MdtColors.YELLOW_BLACK: (curses.COLOR_YELLOW, curses.COLOR_BLACK),
}

DEFAULT_CURSE_COLOR = MdtColors.WHITE_BLACK
BASH_TERM_RESET_COLOR = "\033[00;39;49m"

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
        terminal_color_code = BASH_COLOR_MAP["reset"]
        curses_color_code = CONFIG_COLOR_MAP["reset"]

        # Check if we have a valid color entry for this match
        if match_entry[1] != "":
            if match_entry[1] in BASH_COLOR_MAP:
                terminal_color_code = BASH_COLOR_MAP[match_entry[1]]
            if match_entry[1] in CONFIG_COLOR_MAP:
                curses_color_code = CONFIG_COLOR_MAP[match_entry[1]]

        match_config_list.append(
            ConfigEntry(pattern, terminal_color_code, curses_color_code, match_entry[2])
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
