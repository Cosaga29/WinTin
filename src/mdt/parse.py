#!/usr/bin/env python

import logging
import curses
import time
import os
import re

from definitions import (
    RoomInfo,
    EntityInfo,
    NUMBER_MAP,
    DIRECTION_MAP,
    IGNORE_TOKENS,
)
from config import (
    USER_MATCHES,
    MDT_PARSE_DIR,
    MIN_ROOM_VALUE,
    DEFAULT_NPC_VALUE,
    CURSES_COLOR_PAIR_MAP,
    MdtColors,
)

from patterns import (
    TINTIN_ARRAY_BEGIN,
    TINTIN_ARRAY_BETWEEN,
    MDT_COMMAND_QUEUE,
    PLAYER_COLOR
)


logging.basicConfig(
    filename="crash.mdt.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
_LOGGER = logging.getLogger(__name__)


def filter_exits(lines: list[str]) -> list[str]:
    num_lines = len(lines)
    to_return = []
    current_idx = 0
    while current_idx < num_lines:
        line = lines[current_idx]
        if line.startswith(IGNORE_TOKENS):
            follow_on_direction = True
            # If line starts with any of these, remove it and any follow on directions...
            while follow_on_direction and current_idx+1 < num_lines:
                next_line = lines[current_idx+1]
                words = next_line.split(" ")
                if len(words) == 1 and words[0] in DIRECTION_MAP:
                    current_idx += 1
                elif len(words) >= 2 and words[0] in NUMBER_MAP and words[1] in DIRECTION_MAP:
                    current_idx += 1
                else:
                    follow_on_direction = False
        else:
            to_return.append(line)
        
        current_idx += 1

    return to_return


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
        tt_array (str): The tintin array string

    Returns:
        str: The transformed string
    """
    end_punctuation = tt_array.rfind(".")
    previous_punctuation = max(
        [
            0,
            tt_array.rfind(".", 0, end_punctuation),
            tt_array.rfind("!", 0, end_punctuation),
            tt_array.rfind("?", 0, end_punctuation),
        ]
    )

    last_sentence = tt_array[previous_punctuation + 1 : end_punctuation]

    # Replace {101} with " "
    mdt_line = re.sub(TINTIN_ARRAY_BETWEEN, " ", last_sentence)
    mdt_line = re.sub(TINTIN_ARRAY_BEGIN, "", mdt_line)

    # TODO: If this isn't good enough to catch all data that could potentialy
    # arrive between map door text and the output file being written, we'll
    # have to make the above regex a bit smarter
    mdt_line = re.sub(MDT_COMMAND_QUEUE, "", mdt_line, count=1)

    return mdt_line.lstrip().rstrip().lstrip("{").rstrip("}")


def push_directions(dir_token_string: str, directions: list[tuple[int, str]]) -> bool:
    is_last_dir = False

    # Handles the 1 west, 1 south and 1 east case
    # Note that 'and' is not a descriptor for direction, so this is safe to do unlike for entities
    if "and" in dir_token_string:
        is_last_dir = True

    dir_token_string = dir_token_string.replace(" and ", ", ")
    room_directions = dir_token_string.split(", ")

    for dir in room_directions:
        space = dir.find(" ")
        dir_count_token = dir[:space]
        dir_token = dir[space + 1 :]

        if dir_count_token in NUMBER_MAP:
            dir_number = NUMBER_MAP[dir_count_token]

        if dir_token in DIRECTION_MAP:
            dir_token = DIRECTION_MAP[dir_token]

        # The room where these NPCs are
        directions.append((dir_number, dir_token))

    return is_last_dir


def push_entities(entity_token_string: str, entity_stack: list[EntityInfo]):
    """Method that adds the entity token string to the MDT room data using the entities that
    have not been associated.

    Args:
        entity_token_string (str): The entity string
        entity_stack (list[EntityInfo]): The list of entities that we've seen so far
    """
    # an adorable slave, a grey and blue rat and a grinning young man and two strong men and a blue and purple man

    # Separate entities by 'and'
    entity_token_string = entity_token_string.split(" and ")

    # General method is to parse through the entity string until we encounter a count
    # each entity is associated with a count, unless it's a named
    for entity in entity_token_string:
        e = EntityInfo()
        e.count = 1

        # See if this entity has special codes associated with it
        if entity.startswith("\x1b"):
            # Check that the code matches a player coloring code
            if s := re.search(PLAYER_COLOR, entity):
                if len(s.groups()) > 0:
                    e.count = 1
                    e.description = s.groups()[0]
                    e.curse_color_code = MdtColors.GREEN.value
        else:
            for word in entity.split(" "):
                if word in NUMBER_MAP:
                    e.count = NUMBER_MAP[word]
                    e.description += f"{word} "
                else:
                    e.description += f"{word} "

            e.description = e.description.rstrip()
        entity_stack.append(e)


def calculate_mdt(line: str) -> dict[tuple[tuple[int, str]], RoomInfo]:
    """Calculates the room MDT from the initial string.

    TODO: Convert this into a state machine. It's much more suitable.

    Args:
        line (str): The entity MDT list

    Returns:
        list[str]: The
    """
    # Convert everything to lowercase for matching purposes
    line = line.lower()

    # Helps with tokenizing entities and directions
    # 'two hops are southeast' is logically equivalent to 'two hops is southeast', just bad english
    line = line.replace("are", "is")
    line = line.replace("and the limit of your vision", ", the limit of your vision")

    # Commas are the main tokens that can be used to identify room elements
    lines = line.split(", ")

    # Remove room entries that we don't care about (along with their directions!)
    lines = filter_exits(lines)

    # Master MDT data struct that stores room information parsed from MDT text
    mdt_data: dict[tuple[tuple[int, str]], RoomInfo] = {}

    # Stack used to track entities seen that do not have an immediate direction context
    entity_stack: list[EntityInfo] = []
    direction_stack: list[tuple[int, str]] = []

    current_token_idk = 0
    while current_token_idk < len(lines):
        try:
            line = lines[current_token_idk].rstrip().lstrip()

            # Separates the entities and their respective rooms
            # A cobbler is one west and one southwest
            fragments = line.split(" is ")
            room_entities = fragments[0]

            # If we have entities associated with a room, we'll add the room and entities now
            if len(fragments) == 2:
                room_directions = fragments[1]

                # Calculate the room directions using the room description
                is_last_dir = push_directions(room_directions, direction_stack)

                # Add the so-far parsed entities
                push_entities(room_entities, entity_stack)

                # Before we add the room, check to see if the we have follow on directions
                # 'a handsome hoplite and a fearless hoplite is two east', 'one west', 'and one southeast'
                while not is_last_dir and current_token_idk + 1 < len(lines):
                    direction_string = False

                    # Similar to above, check to see if we have direction information in this line
                    fragments = lines[current_token_idk + 1].split(" is ")

                    # The only case we care about is rogue directions
                    if len(fragments) == 1:

                        # one south and two west
                        fragments = lines[current_token_idk + 1].split(" and ")

                        # northeast and south of one west - line doesnt start with a count so not
                        # a valid direction reference for the current entity stack
                        if len(fragments) > 0 and fragments[0] in DIRECTION_MAP:
                            break

                        # ["one south", "two west"]
                        for frag in fragments:
                            words = frag.split(" ")
                            if len(words) >= 2:
                                # Ensure for each direction listed, we have a valid number and direction
                                if words[0] in NUMBER_MAP and words[1] in DIRECTION_MAP:
                                    # Flag this line as a parsed direction string so we can skip the line on the next iteration
                                    direction_string = True
                                    # This should be associated with the room directions
                                    push_directions(frag, direction_stack)

                        if direction_string:
                            current_token_idk += 1
                        else:
                            # Otherwise it's an entity and we'll parse it on the next iteration
                            break
                    else:
                        # Next line is the normal case (entity + direction, we'll handle it on the next iter)
                        break

                # At this point we are confirmed done with parsing associated directions for this room
                mdt_data[tuple(direction_stack)] = RoomInfo()
                mdt_data[tuple(direction_stack)].entities.extend(entity_stack)
                entity_stack.clear()
                direction_stack.clear()
            else:
                # We need to see if this is a direction description or an entity description
                word_idx = room_entities.find(" ")
                if word_idx == -1:
                    current_token_idk += 1
                    continue
                word = room_entities[:word_idx]

                # Follow on directions are handled above, also they have no meaning since they don't
                # have a count... Skip.
                if word in DIRECTION_MAP:
                    current_token_idk += 1
                    continue

                # i.e. "a shy girl", "a small boy", "a hoplite and a rat", "is" ....
                # Add the entity to the stack and associate it with the directions once we reach it
                if word in NUMBER_MAP:
                    # Check second word to make sure this isn't a direction
                    second_word_idx = room_entities.find(" ", word_idx + 1)
                    if second_word_idx != -1:
                        second_word = room_entities[word_idx + 1 : second_word_idx]
                        # If this is a direction and it doesn't have the context of a previously parsed entity...
                        # Skip.
                        if second_word in DIRECTION_MAP and len(entity_stack) == 0:
                            current_token_idk += 1
                            continue

                # Otherwise, this could be a named entity or a player
                push_entities(room_entities, entity_stack)

            current_token_idk += 1
        except:
            current_token_idk += 1

    return mdt_data


def write_rooms(room_data: dict[tuple[int, str], RoomInfo]):
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
                if (
                    isinstance(match.pattern, str)
                    and match.pattern in entity.description
                ) or (
                    isinstance(match.pattern, re.Pattern)
                    and match.pattern.match(entity.description)
                ):
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


def run_parser(lines: list[str]) -> list[str]:
    # The output from tt++ is always a single line
    try:
        mdt_line = lines[0]
        if is_tintin_array(mdt_line):
            # Parses the last element of the tintin array output as the
            # manual map door text line
            mdt_line = transform_tintin_array(mdt_line)

        mdt_data = calculate_mdt(mdt_line)
        room_data = apply_match_configs(mdt_data)
        write_rooms(room_data)
    except Exception as e:
        _LOGGER.error(e)
        write_rooms({})


def watch_files(filename: str):
    last_update_time = os.stat(filename).st_mtime

    with open("test/mapdoortext.log") as f:
        run_parser(f.readlines())
        return

    with open(filename, "r") as f:
        while True:
            new_time = os.stat(filename).st_mtime

            # If the files modified time has changed, run the parser
            if new_time != last_update_time:
                last_update_time = new_time
                run_parser(f.readlines())
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
        _LOGGER.error(e)
    finally:
        # Cleanup
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
