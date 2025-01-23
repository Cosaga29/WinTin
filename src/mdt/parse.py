#!/usr/bin/env python

import time
import os
import re
from dataclasses import dataclass, field

from maps import NUMBER_MAP, DIRECTION_MAP, TERMINAL_RESET_COLOR
from config import CONFIG, USER_MATCHES, MDT_PARSE_DIR

EXIT_TOKENS = (
    "exit",
    "doors ",
    "a door ",
    "exits ",
    "an exit ",
    "a hard to see through exit ",
    "limit of your",
)


@dataclass
class RoomInfo:
    score: int = 0
    entities: list[str] = field(default_factory=list)


def is_tintin_array(line) -> bool:
    # tt++ arrays have the format {1}text{2}text
    return line[0] == "{" and line[2] == "}"


def find_npc_start_location_index(lines: list[str]) -> int:
    # Look for the first entry in the map door text list that involves the current room.
    # This removes the ASCII map and other unwanted data from the list
    for i in reversed(range(len(lines))):
        if "[" and "]" in lines[i]:
            return i

    return -1


def handle_tintin_array(mdt_line: str) -> str:
    if is_tintin_array(mdt_line):
        mdt_text = ""

        # Split out TinTin array into a list
        lines = re.split("{|}", mdt_line)
        npc_locations_start_idx = find_npc_start_location_index(lines)

        # Pattern match things standing around in other rooms
        for i in range(npc_locations_start_idx, len(lines)):
            if "is standing" in lines[i]:
                continue

            line = lines[i].replace("are", "is")

            # Look for 'NPC is some_distance from here.
            if (
                len(line) > 0
                and line[0].isalpha()
                and re.match(r".*is (one|two|three|four|five).*|.* from here.", line)
            ):
                mdt_text += line + " "

        if len(mdt_text) > 0:
            return mdt_text

    # Effectively do nothing
    return mdt_line


def tokenize(line: str) -> list[str]:
    line = line.lower()
    line = line.replace(" are ", " is ")
    line = line.replace(" black and white ", " black white ")
    line = line.replace(" brown and white ", " brown white ")
    line = line.replace("the limit of your vision is ", "the limit of your vision:")
    line = line.replace(" and ", ", ")
    line = line.replace(" is ", ", ")

    return line.split(", ")


def get_quantity(token: str) -> int:
    if token in NUMBER_MAP:
        return NUMBER_MAP[token]
    for nm_key in NUMBER_MAP:
        if entry.startswith(nm_key):
            quantity = NUMBER_MAP[nm_key]
            entry = entry[len(nm_key) :]
            break


def get_token_context(token: str) -> dict:
    direction = None
    count = None
    token_mentions_direction = False

    entity = ""

    for sub_token in token.split(" "):
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
            entity += sub_token + " "

    return direction, count, entity[:-1]


def write_rooms(room_data: dict[tuple[int, str], RoomInfo]):
    def calc_longest_room_dir_length(room_data: dict):
        longest_dir = -1
        for room_dir in room_data.keys():
            dir_str = ""
            # 1 s, 2 sw
            for dir in room_dir:
                dir_str += f"{dir[0]} {dir[1]}, "

            longest_dir = max(longest_dir, len(dir_str))

        return longest_dir

    # Ensure that all the directions line up in the output
    room_direction_width = calc_longest_room_dir_length(room_data)

    for room_dir, room_info in sorted(
        room_data.items(), key=lambda x: x[1].score, reverse=True
    ):
        output = ""
        for dir in room_dir:
            output += f"{dir[0]} {dir[1]}, "
        output = output[:-2]

        line = "{{:<{}}} [{{}}] ".format(room_direction_width)
        line = line.format(output, room_info.score)
        line = "{} {}".format(line, ", ".join(room_info.entities))
        print(line)

    return


def apply_match_configs(
    room_data: dict[tuple[int, str], RoomInfo]
) -> dict[tuple[int, str], RoomInfo]:
    for room in room_data.values():
        room_score = 0

        for i, entity in enumerate(room.entities):
            # There has got to be a more efficient way of doing this
            matched = False
            entity_score = CONFIG["default_npc_value"]
            entity_with_color = (
                f"{TERMINAL_RESET_COLOR}{room.entities[i]}{TERMINAL_RESET_COLOR}"
            )

            for match in USER_MATCHES:
                # If pattern is a string, just search in string
                if (isinstance(match.pattern, str) and match.pattern in entity) or (
                    isinstance(match.pattern, re.Pattern)
                    and match.pattern.match(entity)
                ):
                    entity_score = match.score
                    entity_with_color = f"{match.terminal_color_code}{room.entities[i]}{TERMINAL_RESET_COLOR}"
                    break

            room.entities[i] = entity_with_color
            room_score += entity_score

        room.score = room_score

    # Filter Rooms that are below min score
    filtered_rooms = {
        k: v for k, v in room_data.items() if v.score > CONFIG["minimum_room_value"]
    }
    return filtered_rooms


def run_parser(lines: list[str]) -> list[str]:
    # The output from tt++ is always a single line
    line = lines[0]
    mdt_line = handle_tintin_array(line)

    # Tokenize
    mdt_tokens = tokenize(mdt_line)

    # Room data is all unique room locations associated with their score and entity list
    room_data: dict[tuple[int, str], RoomInfo] = {}

    subjects = []
    directions = []

    for token in mdt_tokens:
        # Skip entries only involving exists
        if token.startswith(EXIT_TOKENS) or "the limit of your" in token:
            if len(subjects) > 0 and len(directions) > 0:
                # Note that a direction should always follow a subject or list of subjects
                # i.e.  ["a fearless hoplite", "is one southwest"]
                # i.e.2 ["a venerable priest", "a sleepy tortoise", "are one north"]
                # i.e.3 ["a large black hen", "a black-haired old cobbler", "are one northwest", "one north"]
                # A room is defined by its direction and counts in that direction to get to the room
                unique_dir_key = tuple(directions)

                if unique_dir_key not in room_data:
                    room_data[unique_dir_key] = RoomInfo(score=-1, entities=[])

                room_data[unique_dir_key].entities.extend(subjects)
                subjects.clear()
                directions.clear()
        else:
            # Break the token into its directions, counts, subject
            direction, count, subject = get_token_context(token)
            if len(subject) > 0 and count is not None:
                # TODO: Determine if we should include a count of the subject in the result
                subjects.append(f"{subject}")
            elif len(subjects) > 0 and direction is not None and count is not None:
                directions.append((count, direction))

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
                # run_parser([t4])
                run_parser(f.readlines())
                f.seek(0)

            time.sleep(0.5)


if __name__ == "__main__":
    mdt_log_path = os.path.abspath(
        os.path.join(MDT_PARSE_DIR, "../../logs/mapdoortext.log")
    )
    watch_files(mdt_log_path)
