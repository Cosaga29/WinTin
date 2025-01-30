#!/usr/bin/env python

import time
import logging
import curses
import os

from definitions import (
    RoomInfo,
)
from config import (
    USER_MATCHES,
    MDT_PARSE_DIR,
    MIN_ROOM_VALUE,
    DEFAULT_NPC_VALUE,
    CURSES_COLOR_PAIR_MAP,
    MdtColors,
)
from tintin import transform_tintin_array, is_tintin_array
from parser import MdtContextParser

logging.basicConfig(
    filename="crash.mdt.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
_LOGGER = logging.getLogger(__name__)


def write_rooms_to_console(
    stdscr: curses.window, room_data: dict[tuple[int, str], RoomInfo]
):
    """Writes the rooms to the terminal.

    Args:
        room_data (dict[tuple[int, str], RoomInfo]): The room data to write
    """
    stdscr.clear()
    y = 0
    x = 0

    if len(room_data) == 0:
        stdscr.addstr(y, x, "Nothing seen!")
        stdscr.refresh()
        return

    def calc_longest_room_dir_length(room_data: dict):
        longest_dir = -1
        for room_dir in room_data.keys():
            dir_str = ""
            # 1 s, 2 sw
            for dir in room_dir:
                dir_str += f"{dir[0]} {dir[1]},"

            longest_dir = max(longest_dir, len(dir_str))

        return longest_dir

    max_y, max_x = stdscr.getmaxyx()

    # Ensure that all the directions line up in the output
    score_pos_offset = calc_longest_room_dir_length(room_data)

    stdscr.clear()
    y = 0
    for room_dir, room_info in sorted(
        room_data.items(), key=lambda x: x[1].score, reverse=True
    ):
        if y >= max_y:
            break

        x = 0
        for i, dir in enumerate(room_dir):
            dir_str = (
                f"{dir[0]} {dir[1]}"
                if i == len(room_dir) - 1
                else f"{dir[0]} {dir[1]},"
            )
            if x + len(dir_str) < max_x:
                stdscr.addstr(y, x, dir_str)
                x += len(dir_str)
            else:
                break

        room_score_str = f"[{room_info.score}] "
        x = score_pos_offset

        if x + len(room_score_str) < max_x:
            # Add the [score]
            stdscr.addstr(
                y, x, room_score_str, curses.color_pair(MdtColors.CYAN_BLACK.value)
            )
            x += len(room_score_str)
        else:
            break

        for i, entity in enumerate(room_info.entities):
            entity_str = (
                f"{entity.description}"
                if i == len(room_info.entities) - 1
                else f"{entity.description}, "
            )

            if x + len(entity_str) < max_x:
                stdscr.addstr(
                    y, x, entity_str, curses.color_pair(entity.curse_color_code)
                )
                x += len(entity_str)
            else:
                break

        y += 1

    stdscr.refresh()


def apply_match_configs(
    room_data: dict[tuple[tuple[int, str]], RoomInfo]
) -> dict[tuple[tuple[int, str]], RoomInfo]:
    """Applys the user config regex matches to rooms parsed from the MDT information.
    Scores the entities in the associated rooms.
    Associates colors with each entity in the room.

    Args:
        room_data (dict[tuple[int, str], RoomInfo]): The parsed rooms

    Returns:
        dict[tuple[int, str], RoomInfo]: The filtered, colored and scored rooms
    """
    for room_info in room_data.values():
        room_score = 0

        for entity in room_info.entities:
            # There has got to be a more efficient way of doing this
            entity_score = DEFAULT_NPC_VALUE

            for match in USER_MATCHES:
                # If pattern is a string, just search in string
                if match.is_regex:
                    if match.pattern.match(entity.description):
                        # Score = score per entity * entity count
                        entity.score = match.score
                        entity_score = match.score * entity.count
                        entity.curse_color_code = match.curses_color_code
                        break
                else:
                    if match.pattern in entity.description:
                        # Score = score per entity * entity count
                        entity.score = match.score
                        entity_score = match.score * entity.count
                        entity.curse_color_code = match.curses_color_code
                        break

            room_score += entity_score

        room_info.score = room_score

    # Filter Rooms that are below min score
    filtered_rooms = {k: v for k, v in room_data.items() if v.score >= MIN_ROOM_VALUE}

    # TODO: Sort rooms right above this line to optimize how many NPC lists we need to sort
    for info in filtered_rooms.values():
        info.entities.sort(key=lambda x: x.score, reverse=True)

    return filtered_rooms


def to_mdt_rooms(stdscr: curses.window, lines: list[str]) -> list[str]:
    # The output from tt++ is always a single line
    try:
        mdt_data = {}
        if len(lines) > 0:
            mdt_line = lines[0]
            if is_tintin_array(mdt_line):
                # Parses the last element of the tintin array output as the
                # manual map door text line
                mdt_line = transform_tintin_array(mdt_line)

            reader = MdtContextParser(mdt_line)
            mdt_data = reader.read()
            mdt_data = apply_match_configs(mdt_data)
        write_rooms_to_console(stdscr, mdt_data)
    except Exception as e:
        _LOGGER.error("Exception while parsing MDT lines!")
        _LOGGER.error(e)
        _LOGGER.error("------------MDT------------")
        _LOGGER.error(lines[0])
        _LOGGER.error("------------MDT------------")
        write_rooms_to_console(stdscr, {})


def main(stdscr: curses.window, filename: str):
    curses.curs_set(0)

    last_update_time = os.stat(filename).st_mtime

    # TESTING ONLY
    # with open("test/mapdoortext.log") as f:
    #    to_mdt_rooms(f.readlines())
    #    pass

    # Initialize MDT color pairs after we've initialized the curse screen
    for mdt_color, curses_color_pair in CURSES_COLOR_PAIR_MAP.items():
        curses.init_pair(mdt_color.value, curses_color_pair[0], curses_color_pair[1])

    with open(filename, "r") as f:
        while True:
            new_time = os.stat(filename).st_mtime

            # If the files modified time has changed, run the parser
            if new_time != last_update_time:
                last_update_time = new_time
                to_mdt_rooms(stdscr, f.readlines())
                f.seek(0)

            time.sleep(0.2)


if __name__ == "__main__":
    try:
        mdt_log_path = os.path.abspath(
            os.path.join(MDT_PARSE_DIR, "../../logs/mapdoortext.log")
        )

        curses.wrapper(main, mdt_log_path)
    except Exception as e:
        _LOGGER.error(e)