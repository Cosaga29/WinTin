#!/usr/bin/env python

import curses
import time
import os
import re

from definitions import RoomInfo, TokenType, NUMBER_MAP, DIRECTION_MAP, EXIT_TOKENS
from config import (
    USER_MATCHES,
    MDT_PARSE_DIR,
    DEFAULT_CURSE_COLOR,
    MIN_ROOM_VALUE,
    DEFAULT_NPC_VALUE,
    CURSES_COLOR_PAIR_MAP,
)


from test_data import T4, T5


TINTIN_ARRAY_START = re.compile(r"({\d+})|(})|({)")
TINTIN_ARRAY_END = re.compile(r"}")


def is_tintin_array(line: str) -> bool:
    """Determines if the line is a tt array. Arrays start with {1}

    Args:
        line (str): The line

    Returns:
        bool: If the line is a tintin array
    """
    # tt++ arrays have the format {1}text{2}text
    return line[0] == "{" and line[2] == "}"


def transform_tintin_array(tt_array: str) -> str:
    """Stringifys the tintin array to a normal string.

    Args:
        mdt_line (str): The tintin array string

    Returns:
        str: The transformed string
    """
    mdt_line = re.sub(TINTIN_ARRAY_START, " ", tt_array)
    end_punctuation = tt_array.rfind(".")
    previous_punctuation = max([0, tt_array.rfind(".", 0, end_punctuation), tt_array.rfind("!", 0, end_punctuation), tt_array.rfind("?", 0, end_punctuation)])

    return mdt_line[previous_punctuation+1:end_punctuation]


def tokenize(line: str) -> list[str]:
    #def matcher(match: re.Match):
    #    if match.groups()[0] in NUMBER_MAP:
    #        return NUMBER_MAP[match.groups()[0]]
    #    return match.groups()[0]

    line = line.lower()
    line = line.replace("are", "is")
    lines = line.split(", ")
    no_exit_lines = list(filter(lambda x: not x.startswith(EXIT_TOKENS), lines))
    room_entities = []
    directions = []
    rooms = {}
    for token in no_exit_lines:
        fragments = token.split(" is ")
        if len(fragments) >= 2:
            room_entities.append(fragments[0])
            directions.append(fragments[1])

    # Numerify entities
    for i, entity_list_str in enumerate(room_entities):
        token_stack = []

        # Note that we have to split the 'and' context here because we could have
        # 'entity and entity2' or 'blue and red entity'
        matches = re.findall(r"and ([a-z]+)", entity_list_str)

        if matches:
            current_token_count = 0
            current_entity_description = ""
            for token in entity_list_str.split(" and "):
                words = token.split(" ")
                if words[0] in NUMBER_MAP:
                    # Push our old token
                    if current_token_count > 0:
                        token_stack.append((current_token_count, current_entity_description))

                    # New token!
                    current_token_count = NUMBER_MAP[words[0]]
                    current_entity_description = token
                else:
                    current_entity_description += f" {token}"
        
            token_stack.append((current_token_count, current_entity_description))
        else:
            words = entity_list_str.split(" ")
            token_stack.append((NUMBER_MAP[words[0]], entity_list_str))

        print('here')



    print('here')

    # TODO: Regex multiple per pass
    line = line.replace("queued command: map door text", "")
    line = line.replace(" black and white ", " black white ")
    line = line.replace(" brown and white ", " brown white ")
    line = line.replace("the limit of your vision is ", "the limit of your vision:")

    t = r" and (.*) "
    matches = re.findall(t, line)
    for match in matches:
        print(match)


    line = re.sub(r"( and (.*) )|( and an )", ", a ", line)
    #line = line.replace(" and ", ", ")
    line = line.replace(" is ", ", ")

    return line.split(", ")


def get_token_context(token: str) -> tuple[str | None, int | None, str, TokenType]:
    """Parses the token string to determine if it references an entity or a direction.

    Args:
        token (str): The token string

    Returns:
        tuple[str | None, int | None, str, TokenType]: Tuple containing the tokenized context
    """
    direction = None
    count = None
    token_mentions_direction = False
    token_type = TokenType.DIRECTION

    entity = ""

    for sub_token in token.split(" "):
        if not sub_token:
            continue

        if sub_token in DIRECTION_MAP:
            direction = str(DIRECTION_MAP[sub_token])
            token_mentions_direction = True
            continue
        if sub_token in NUMBER_MAP:
            # Mention of a count
            count = NUMBER_MAP[sub_token]
            continue

        # If this token doesn't mention direction, assume it's about an entity
        if not token_mentions_direction:
            token_type = TokenType.ENTITY
            entity += sub_token + " "

    return direction, count, entity[:-1], token_type


def write_rooms(room_data: dict[tuple[int, str], RoomInfo]):
    """Writes the rooms to the terminal.

    Args:
        room_data (dict[tuple[int, str], RoomInfo]): The room data to write
    """

    def calc_longest_room_dir_length(room_data: dict):
        longest_dir = -1
        for room_dir in room_data.keys():
            dir_str = ""
            # 1 s, 2 sw
            for dir in room_dir:
                dir_str += f"{dir[0]} {dir[1]}, "

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
            stdscr.addstr(y, x, dir_str)
            x += len(dir_str)

        room_score_str = f"[{room_info.score}] "
        x = score_pos_offset
        stdscr.addstr(y, x, room_score_str)

        x += len(room_score_str)
        for i, entity in enumerate(room_info.entities):
            entity_str = (
                f"{entity}" if i == len(room_info.entities) - 1 else f"{entity}, "
            )
            stdscr.addstr(y, x, entity_str, curses.color_pair(room_info.colors[i]))
            x += len(entity_str)

        y += 1

    stdscr.refresh()


def apply_match_configs(
    room_data: dict[tuple[int, str], RoomInfo]
) -> dict[tuple[int, str], RoomInfo]:
    """Applys the user config regex matches to rooms parsed from the MDT information.
    Scores the entities in the associated rooms.
    Associates colors with each entity in the room.

    Args:
        room_data (dict[tuple[int, str], RoomInfo]): The parsed rooms

    Returns:
        dict[tuple[int, str], RoomInfo]: The filtered, colored and scored rooms
    """
    for room in room_data.values():
        room_score = 0

        for entity in room.entities:
            # There has got to be a more efficient way of doing this
            entity_score = DEFAULT_NPC_VALUE
            entity_curse_color = DEFAULT_CURSE_COLOR

            for match in USER_MATCHES:
                # If pattern is a string, just search in string
                if (isinstance(match.pattern, str) and match.pattern in entity) or (
                    isinstance(match.pattern, re.Pattern)
                    and match.pattern.match(entity)
                ):
                    entity_score = match.score
                    entity_curse_color = match.curses_color_code
                    break

            room_score += entity_score
            room.colors.append(entity_curse_color)

        room.score = room_score

    # Filter Rooms that are below min score
    filtered_rooms = {k: v for k, v in room_data.items() if v.score >= MIN_ROOM_VALUE}
    return filtered_rooms


def run_parser(lines: list[str]) -> list[str]:
    # The output from tt++ is always a single line
    mdt_line = lines[0]
    if is_tintin_array(mdt_line):
        mdt_line = transform_tintin_array(mdt_line)

    mdt_tokens = tokenize(mdt_line)

    # Room data is all unique room locations associated with their score and entity list
    room_data: dict[tuple[int, str], RoomInfo] = {}

    subjects = []
    directions = []
    last_token = TokenType.NONE

    def add_room(
        subjects: list, directions: list, room_data: dict[tuple[int, str], RoomInfo]
    ):
        if len(subjects) == 0 and len(directions) == 0:
            return

        unique_dir_key = tuple(directions)

        if unique_dir_key not in room_data:
            room_data[unique_dir_key] = RoomInfo(score=-1, entities=[])

        room_data[unique_dir_key].entities.extend(subjects)
        subjects.clear()
        directions.clear()

    for token in mdt_tokens:
        # The MDT output involves series of tokens. The tokens are classified as either
        # having an entity or having a direction. The parser works on the assumption that
        # discworld will group entities and directions together i.e.
        # "a large man, a large woman, are 2 south, 2 southwest".
        # The parsing of a room is 'complete' once we hit an exist token, OR
        # if the the last token we parsed was a direction and the new one is an entity
        if token.startswith(EXIT_TOKENS) or "the limit of your" in token:
            if len(subjects) > 0 and len(directions) > 0:
                add_room(subjects, directions, room_data)
        else:
            # Break the token into its directions, counts, subject
            direction, count, subject, this_token = get_token_context(token)

            if last_token == TokenType.DIRECTION and this_token == TokenType.ENTITY:
                # We're done with the old room
                add_room(subjects, directions, room_data)
                subjects.append(subject)
                last_token = this_token
                continue

            # Otherwise we're still building the room definition
            if this_token == TokenType.DIRECTION:
                directions.append((count, direction))

            if this_token == TokenType.ENTITY:
                subjects.append(subject)

            last_token = this_token

    room_data = apply_match_configs(room_data)
    write_rooms(room_data)


def watch_files(filename: str):
    last_update_time = os.stat(filename).st_mtime

    with open(filename, "r") as f:
        while True:
            new_time = os.stat(filename).st_mtime

            # If the files modified time has changed, run the parser
            if new_time != last_update_time:
                last_update_time = new_time
                run_parser([T5])
                #run_parser(f.readlines())
                f.seek(0)

            time.sleep(0.2)


if __name__ == "__main__":
    try:
        stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)

        # Initialize MDT color pairs after we've initialized the curse screen
        for mdt_color, curses_color_pair in CURSES_COLOR_PAIR_MAP.items():
            curses.init_pair(
                mdt_color.value, curses_color_pair[0], curses_color_pair[1]
            )

        mdt_log_path = os.path.abspath(
            os.path.join(MDT_PARSE_DIR, "../../logs/mapdoortext.log")
        )
        watch_files(mdt_log_path)
    except Exception as e:
        print(e)
    finally:
        # Cleanup
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
