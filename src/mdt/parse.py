#!/usr/bin/env python

from typing import NamedTuple
from dataclasses import dataclass, field
import time
import os
import re
import sys
import math
import json

from maps import NUMBER_MAP, DIRECTION_MAP, COLOR_MAP

t1 = "An exit south of one southwest, a fearless hoplite is one southwest, the limit of your vision is one southwest from here, an exit north of one north and the limit of your vision is one north from here."
t2 = "{1}{A fearless hoplite is one southwest, the limit of your vision is one southwest from here and the limit of your vision is one north}{2}{from here.}"
t3 = "An exit east of one south, a brawny athlete, a cute boy and a stressed bureaucrat are one south, exits south and north of one east, a careful slave is one east, an exit east of one north, a venerable priest and a sleepy tortoise are one north, exits southwest, southeast and north of one south and one southeast, the limit of your vision is one south and one southeast from here, exits east, southwest and northwest of two east, an enchanting lady is two east, the limit of your vision is two east from here, an exit south of one north and one northeast and the limit of your vision is one north and one northeast from here.\n"
t4 = "A sniffy young woman is one west, exits northeast and south of one northwest, a thin hawker and a grumpy old stallowner are one northwest, exits southeast, south and north of one southwest, a tired bureaucrat and a large brown rooster are one southwest, the limit of your vision is one southwest from here, exits west and southwest of one north, a small boy is one north, an exit east of one west and one northwest, an old cobbler is one west and one northwest, the limit of your vision is one west and one northwest from here, a door south of two west, exits north, northeast and southeast of two west, a fat yellow rooster is two west, the limit of your vision is two west from here, an exit south of two northwest, the limit of your vision is two northwest from here, exits southwest, southeast and west of one northwest and one north, a skittish brown hen, a large black hen and a black-haired old cobbler are one northwest and one north, the limit of your vision is one northwest and one north from here, a door east of two north, exits west and southwest of two north and the limit of your vision is two north from here.\n"


EXIT_TOKENS = ('exit', 'doors ', 'a door ', 'exits ', 'an exit ', 'a hard to see through exit ', 'limit of your')


class RoomInfo(NamedTuple):
    score: int = 0
    entities: list[str] = []


MDT_PARSE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load the JSON configuration file
with open(os.path.join(MDT_PARSE_DIR, "config.json"), 'r') as config_file:
    CONFIG = json.load(config_file)

CUSTOM_MATCHES = []


for match in CONFIG['custom_matches']:
    if len(match) > 1:
        CUSTOM_MATCHES.append(match)

DEFAULT_NPC_VALUE = CONFIG['default_npc_value']
BONUS_PLAYER_VALUE = CONFIG['bonus_player_value']
MIN_ROOM_VALUE = CONFIG['minimum_room_value']
SHOW_HIDDEN_ROOM_COUNT = CONFIG['show_hidden_room_count']



def is_tintin_array(line) -> bool:
    # tt++ arrays have the format {1}text{2}text
    return line[0] == '{' and line[2] == '}'


def find_npc_start_location_index(lines: list[str]) -> int:
    # Look for the first entry in the map door text list that involves the current room.
    # This removes the ASCII map and other unwanted data from the list
    for i in reversed(range(len(lines))):
        if '[' and ']' in lines[i]:
            return i
        
    return -1


def handle_tintin_array(mdt_line: str) -> str:
    if is_tintin_array(mdt_line):
        mdt_text = ""

        # Split out TinTin array into a list
        lines = re.split('{|}', mdt_line)
        npc_locations_start_idx = find_npc_start_location_index(lines)

        # Pattern match things standing around in other rooms
        for i in range(npc_locations_start_idx, len(lines)):
            if 'is standing' in lines[i]:
                continue

            line = lines[i].replace('are', 'is')
            
            # Look for 'NPC is some_distance from here.
            if len(line) > 0 and line[0].isalpha() and re.match(r".*is (one|two|three|four|five).*|.* from here.", line):
                mdt_text += line + " "

        if len(mdt_text) > 0:
            return mdt_text
    
    # Effectively do nothing
    return mdt_line


def explode(div, mdt):
    if div == '':
        return False
    pos, fragments = 0, []
    for m in re.finditer(div, mdt):
        fragments.append(mdt[pos:m.start()])
        pos = m.end()
    fragments.append(mdt[pos:])

    test_fragments = mdt.split(", ")

    return fragments


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
            entry = entry[len(nm_key):]
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


def score_rooms(room_data: dict[tuple[int, str], RoomInfo]):
    return


def color_entities(room_data: dict[tuple[int, str], RoomInfo]):
    return


def write_rooms(room_data: dict[tuple[int, str], RoomInfo]):
    for room in room_data:
        print(f"[{}]: - ")
    return


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
    color = ""
    for token in mdt_tokens:
        if token[0:6] == 'u001b[':
            # u001b[38;5;37mRuhsbaaru001b[39;49mu001b[0m
            here = token.index('m')
            color = token[7:here]
            token = token.replace('u001b', '\033')

            # Might be a second colour code for PK
            if token[0:6] == 'u001b[':
                here = token.index('m')
                color = token[7:here]
                token = token[here + 1:-20]


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

                room_data[unique_dir_key].entities.append(", ".join(subjects))
                subjects.clear()
                directions.clear()
        else:
            # Break the token into its directions, counts, subject
            direction, count, subject = get_token_context(token)
            if len(subject) > 0 and count is not None:
                # TODO: Determine if we should include a count of the subject in the result
                subjects.append(f"{count} {subject}")
            elif len(subjects) > 0 and direction is not None and count is not None:
                directions.append((count, direction))
    
    score_rooms(room_data)
    color_entities(room_data)
    write_rooms(room_data)


    #    if entry != "" and ' of a ' not in entry:
    #        exit_strings = ['doors ', 'a door ', 'exits ', 'an exit ', 'a hard to see through exit ']
    #        if entry.startswith(tuple(exit_strings)):
    #            # print('Special exit, ignore this line? next line is processed...')
    #            data['ignoring_exits'] = True
    #        elif entry.startswith('the limit of your vision:'):
    #            if data['last_count'] > 0:
    #                this_square = [data['last_count'], data['last_direction'], data['room_id'], int(math.floor(data['room_value']))]
    #                data['enemies_by_square'].append(this_square)
    #                data['nothing'] = False
    #                data['next_color'] = ''
    #                data['room_id'] = data['room_id'] + 1
    #                data['room_value'] = 0
    #            data['last_direction'] = ''
    #            data['last_enemy_line'] = ''
    #            data['last_count'] = 0
    #            data['last_was_dir'] = 0
    #        else:
    #            # find the quantity first
    #            quantity = 1
    #            for nm_key in NUMBER_MAP:
    #                if entry.startswith(nm_key):
    #                    quantity = NUMBER_MAP[nm_key]
    #                    entry = entry[len(nm_key):]
    #                    break
#
    #            is_direction = 0
    #            this_direction = ''
#
    #            if entry.startswith("northeast"):
    #                is_direction = 1
    #                this_direction = "northeast"
    #            elif entry.startswith("northwest"):
    #                is_direction = 1
    #                this_direction = "northwest"
    #            elif entry.startswith("southeast"):
    #                is_direction = 1
    #                this_direction = "southeast"
    #            elif entry.startswith("southwest"):
    #                is_direction = 1
    #                this_direction = "southwest"
    #            elif entry.startswith("north"):
    #                is_direction = 1
    #                this_direction = "north"
    #            elif entry.startswith("east"):
    #                is_direction = 1
    #                this_direction = "east"
    #            elif entry.startswith("south"):
    #                is_direction = 1
    #                this_direction = "south"
    #            elif entry.startswith("west"):
    #                is_direction = 1
    #                this_direction = "west"
#
    #            if is_direction == 1:
    #                if not data['ignoring_exits']:
    #                    # print('[handling direction, not exits]')
    #                    data['last_was_dir'] = 1
#
    #                    if data['last_direction'] != '':
    #                        data['last_direction'] = '{}, '.format(data['last_direction'])
    #                
    #                    data['last_direction'] = '{}{} {}'.format(
    #                        data['last_direction'], quantity, DIRECTION_MAP[this_direction]
    #                    )
    #                else:
    #                    # print('[ignoring exits direction line]')
    #                    pass
    #            else:
    #                data['ignoring_exits'] = False
    #                if data['last_was_dir'] == 1:
    #                    # reset count
    #                    if data['last_count'] > 0:
    #                        this_square = [data['last_count'], data['last_direction'], data['room_id'], int(math.floor(data['room_value']))]
    #                        data['enemies_by_square'].append(this_square)
    #                        data['nothing'] = False
    #                        data['next_color'] = ''
    #                        data['room_id'] = data['room_id'] + 1
    #                        data['room_value'] = 0
    #                    data['last_direction'] = ''
    #                    data['last_enemy_line'] = ''
    #                    data['last_count'] = 0
    #                    data['last_was_dir'] = 0
#
    #                data['next_color'] = ''
    #                add_player_value = False
#
    #                # Special GMCP MDT colour codes
    #                if entry[0:6] == 'u001b[':
    #                    # u001b[38;5;37mRuhsbaaru001b[39;49mu001b[0m
    #                    here = entry.index('m')
    #                    data['next_color'] = entry[7:here]
    #                    # entry = entry[here + 1:-20]
    #                    # entry = entry.replace('u001b', '')
    #                    entry = entry.replace('u001b', '\033')
#
    #                    # Might be a second colour code for PK
    #                    if entry[0:6] == 'u001b[':
    #                        here = entry.index('m')
    #                        data['next_color'] = entry[7:here]
    #                        entry = entry[here + 1:-20]
    #                    add_player_value = True
#
    #                this_value = self.default_npc_value
#
    #                for custom_match in self.custom_matches:
    #                    if custom_match[3]:
    #                        # This is a regex match
    #                        rexp = re.compile(custom_match[0])
    #                        if rexp.match(entry):
    #                            if custom_match[1] and custom_match[1] in COLOR_MAP:
    #                                entry = '{}{}{}'.format(
    #                                    COLOR_MAP[custom_match[1]],
    #                                    entry,
    #                                    COLOR_MAP['reset']
    #                                )
    #                            this_value = custom_match[2]
    #                    else:
    #                        # This is a regular string match
    #                        if custom_match[0] in entry:
    #                            if custom_match[1] and custom_match[1] in COLOR_MAP:
    #                                entry = '{}{}{}'.format(
    #                                    COLOR_MAP[custom_match[1]],
    #                                    entry,
    #                                    COLOR_MAP['reset']
    #                                )
#
    #                            this_value = custom_match[2]
#
    #                if add_player_value == True:
    #                    this_value = this_value + self.bonus_player_value
#
    #                data['room_value'] = data['room_value'] + (this_value * quantity)
#
    #                if quantity > 1:
    #                    entry = '{} {}'.format(quantity, entry)
    #                data['entity_table'].append([data['room_id'], entry, data['next_color']])
#
    #                data['last_count'] = data['last_count'] + quantity
    #                if data['last_enemy_line'] != '':
    #                    data['last_enemy_line'] = '{}, '.format(data['last_enemy_line'])
    #                data['last_enemy_line'] = '{}{}'.format(data['last_enemy_line'], entry)


    return


def watch_files(filename: str):
    last_update_time = os.stat(filename).st_mtime

    with open(filename, "r") as f:
        while True:
            new_time = os.stat(filename).st_mtime
            
            # If the files modified time has changed, run the parser
            if new_time != last_update_time:
                last_update_time = new_time
                run_parser([t4])
                #run_parser(f.readlines())
                f.seek(0)

            time.sleep(0.5)

class MapDoorText:
    def __init__(self):
        self.return_value = []
        self.custom_matches = []

        # Load the JSON configuration file
        with open('mdtconfig.json', 'r') as config_file:
            config = json.load(config_file)

        # Strip comments from custom matches
        for match in config['custom_matches']:
            if len(match) > 1:
                self.custom_matches.append(match)

        self.default_npc_value = config['default_npc_value']
        self.bonus_player_value = config['bonus_player_value']
        self.minimum_room_value = config['minimum_room_value']
        self.show_hidden_room_count = config['show_hidden_room_count']

    @staticmethod
    def explode(div, mdt):
        if div == '':
            return False
        pos, fragments = 0, []
        for m in re.finditer(div, mdt):
            fragments.append(mdt[pos:m.start()])
            pos = m.end()
        fragments.append(mdt[pos:])
        return fragments

    def parse_mdt(self, mdt_line):
        # Make lower case, do initial replacements
        mdt_line = mdt_line.lower()
        mdt_line = mdt_line.replace(" are ", " is ")
        mdt_line = mdt_line.replace(" black and white ", " black white ")
        mdt_line = mdt_line.replace(" brown and white ", " brown white ")
        mdt_line = mdt_line.replace("the limit of your vision is ", "the limit of your vision:")
        mdt_line = mdt_line.replace(" and ", ", ")
        mdt_line = mdt_line.replace(" is ", ", ")
        mdt_table = self.explode(', ', mdt_line)

        data = {
            'last_direction': '',
            'last_enemy_line': '',
            'last_count': 0,
            'last_was_dir': 0,
            'enemies_by_square': [],
            'ignoring_exits': False,
            'entity_table': [],
            'room_id': 1,
            'room_value': 0,
            'longest_direction': 0,
            'nothing': True,
            'next_color': ''
        }
        exit_strings = ['doors ', 'a door ', 'exits ', 'an exit ', 'a hard to see through exit ']

        for entry in mdt_table:
            if entry != "" and ' of a ' not in entry:
                if entry.startswith(tuple(exit_strings)):
                    # print('Special exit, ignore this line? next line is processed...')
                    data['ignoring_exits'] = True
                elif entry.startswith('the limit of your vision:'):
                    if data['last_count'] > 0:
                        this_square = [data['last_count'], data['last_direction'], data['room_id'], int(math.floor(data['room_value']))]
                        data['enemies_by_square'].append(this_square)
                        data['nothing'] = False
                        data['next_color'] = ''
                        data['room_id'] = data['room_id'] + 1
                        data['room_value'] = 0
                    data['last_direction'] = ''
                    data['last_enemy_line'] = ''
                    data['last_count'] = 0
                    data['last_was_dir'] = 0
                else:
                    # find the quantity first
                    quantity = 1
                    for nm_key in NUMBER_MAP:
                        if entry.startswith(nm_key):
                            quantity = NUMBER_MAP[nm_key]
                            entry = entry[len(nm_key):]
                            break

                    is_direction = 0
                    this_direction = ''

                    if entry.startswith("northeast"):
                        is_direction = 1
                        this_direction = "northeast"
                    elif entry.startswith("northwest"):
                        is_direction = 1
                        this_direction = "northwest"
                    elif entry.startswith("southeast"):
                        is_direction = 1
                        this_direction = "southeast"
                    elif entry.startswith("southwest"):
                        is_direction = 1
                        this_direction = "southwest"
                    elif entry.startswith("north"):
                        is_direction = 1
                        this_direction = "north"
                    elif entry.startswith("east"):
                        is_direction = 1
                        this_direction = "east"
                    elif entry.startswith("south"):
                        is_direction = 1
                        this_direction = "south"
                    elif entry.startswith("west"):
                        is_direction = 1
                        this_direction = "west"

                    if is_direction == 1:
                        if not data['ignoring_exits']:
                            # print('[handling direction, not exits]')
                            data['last_was_dir'] = 1

                            if data['last_direction'] != '':
                                data['last_direction'] = '{}, '.format(data['last_direction'])
                        
                            data['last_direction'] = '{}{} {}'.format(
                                data['last_direction'], quantity, DIRECTION_MAP[this_direction]
                            )
                        else:
                            # print('[ignoring exits direction line]')
                            pass
                    else:
                        data['ignoring_exits'] = False
                        if data['last_was_dir'] == 1:
                            # reset count
                            if data['last_count'] > 0:
                                this_square = [data['last_count'], data['last_direction'], data['room_id'], int(math.floor(data['room_value']))]
                                data['enemies_by_square'].append(this_square)
                                data['nothing'] = False
                                data['next_color'] = ''
                                data['room_id'] = data['room_id'] + 1
                                data['room_value'] = 0
                            data['last_direction'] = ''
                            data['last_enemy_line'] = ''
                            data['last_count'] = 0
                            data['last_was_dir'] = 0

                        data['next_color'] = ''
                        add_player_value = False

                        # Special GMCP MDT colour codes
                        if entry[0:6] == 'u001b[':
                            # u001b[38;5;37mRuhsbaaru001b[39;49mu001b[0m
                            here = entry.index('m')
                            data['next_color'] = entry[7:here]
                            # entry = entry[here + 1:-20]
                            # entry = entry.replace('u001b', '')
                            entry = entry.replace('u001b', '\033')

                            # Might be a second colour code for PK
                            if entry[0:6] == 'u001b[':
                                here = entry.index('m')
                                data['next_color'] = entry[7:here]
                                entry = entry[here + 1:-20]
                            add_player_value = True

                        this_value = self.default_npc_value

                        for custom_match in self.custom_matches:
                            if custom_match[3]:
                                # This is a regex match
                                rexp = re.compile(custom_match[0])
                                if rexp.match(entry):
                                    if custom_match[1] and custom_match[1] in COLOR_MAP:
                                        entry = '{}{}{}'.format(
                                            COLOR_MAP[custom_match[1]],
                                            entry,
                                            COLOR_MAP['reset']
                                        )
                                    this_value = custom_match[2]
                            else:
                                # This is a regular string match
                                if custom_match[0] in entry:
                                    if custom_match[1] and custom_match[1] in COLOR_MAP:
                                        entry = '{}{}{}'.format(
                                            COLOR_MAP[custom_match[1]],
                                            entry,
                                            COLOR_MAP['reset']
                                        )

                                    this_value = custom_match[2]

                        if add_player_value == True:
                            this_value = this_value + self.bonus_player_value

                        data['room_value'] = data['room_value'] + (this_value * quantity)

                        if quantity > 1:
                            entry = '{} {}'.format(quantity, entry)
                        data['entity_table'].append([data['room_id'], entry, data['next_color']])

                        data['last_count'] = data['last_count'] + quantity
                        if data['last_enemy_line'] != '':
                            data['last_enemy_line'] = '{}, '.format(data['last_enemy_line'])
                        data['last_enemy_line'] = '{}{}'.format(data['last_enemy_line'], entry)

        if data['nothing']:
            self.return_value.append('Nothing seen, try elsewhere!')
        else:
            done_here = False
            rooms_ignored = 0

            data['enemies_by_square'].sort(key=lambda square: square[3])

            # Grab shortest
            for square in data['enemies_by_square']:
                # Only show if this room meets the minimum value
                if square[3] >= self.minimum_room_value and len(square[1]) > data['longest_direction']:
                    data['longest_direction'] = len(square[1])

            for square in data['enemies_by_square']:
                # Only show if this room meets the minimum value
                if square[3] >= self.minimum_room_value:
                    done_here = False

                    # add colour to points output
                    square[3] = '{}{}{}'.format(COLOR_MAP['cyan'], square[3], COLOR_MAP['reset'])
                    fstring = '{{:<{}}} [{{}}] '.format(data['longest_direction'])
                    output = fstring.format(square[1], square[3])
                    for entity in data['entity_table']:
                        if entity[0] == square[2]:
                            if done_here:
                                output = '{}, '.format(output)
                            output = '{}{}'.format(output, entity[1])
                            done_here = True
                    if square[0] < 2:
                        output = '{} [{} thing]'.format(output, square[0])
                    else:
                        output = '{} [{} things]'.format(output, square[0])
                    self.return_value.append(output)
                else:
                    rooms_ignored = rooms_ignored + 1

                square = None

            for entity in data['entity_table']:
                entity = None

            if rooms_ignored > 0 and self.show_hidden_room_count:
                output = '({} rooms below your value limit of {})'.format(rooms_ignored, self.minimum_room_value)
                self.return_value.append(output)


def cleanLine(mdt_line: str) -> str:
    if mdt_line[0] == '{' and mdt_line[2] == '}':
        # Assume that we're parsing a TinTin list
        lines = re.split('{|}', mdt_line)
        mdt_text = ""
        start_room_idx = 0

        # Reduce problem set
        for i in reversed(range(len(lines))):
            if '[' and ']' in lines[i]:
                start_room_idx = i

        # Pattern match things standing around in other rooms
        for i in range(start_room_idx, len(lines)):
            if 'is standing' in lines[i]:
                continue

            line = lines[i].replace('are', 'is')
            if len(line) > 0 and line[0].isalpha() and re.match(r".*is (one|two|three|four|five).*|.* from here.", line):
                mdt_text += line + " "

        if len(mdt_text) > 0:
            return mdt_text
        else:
            return ""


    # Find the last sentence in the mdt_line
    line_start = mdt_line.rfind(".", 0, len(mdt_line) - 2)

    return mdt_line[line_start+1:].lstrip()

if __name__ == '__main__':
    mdt_log_path = os.path.abspath(os.path.join(MDT_PARSE_DIR, "../../logs/mapdoortext.log"))
    print(mdt_log_path)
    watch_files(mdt_log_path)

    #if len(sys.argv) < 2:
    #    print('[error] No input provided.')
    #    sys.exit()
#
    #argument, mdt_line = sys.argv.pop(1), None
#
    ## Is this a file passed to us?
    #if os.path.exists(argument):
    #    with open(argument, 'r') as f:
    #        mdt_line = f.readline()
#
    #else:
    #    mdt_line = argument
#
    #mdt = MapDoorText()
    #mdt.parse_mdt(cleanLine(mdt_line))
#
    #mdt.return_value.reverse()
    #for line in mdt.return_value:
    #    print(line)
