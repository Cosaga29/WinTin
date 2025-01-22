#!/usr/bin/env python

from dataclasses import dataclass, field
import time
import os
import re
import sys
import math
import json

from maps import NUMBER_MAP, DIRECTION_MAP, COLOR_MAP



EXIT_TOKENS = ('doors ', 'a door ', 'exits ', 'an exit ', 'a hard to see through exit ')


@dataclass
class Context:
    last_direction: str = field(default="")
    last_enemy_line: str = field(default="")
    last_count: int = field(default=0)
    last_was_dir: int = field(default=0)
    enemies_by_square: list[str] = field(default=[])
    ignoring_exits: bool = field(default=False)
    entity_table: list[str] = field(default=[])
    room_id: int = field(default=1)
    room_value: int = field(default=0)
    longest_direction: int = field(default=0)
    nothing: bool = field(default=True)
    next_color: str = field(default="")


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


def run_initial_replacements(line: str) -> str:
    line = line.lower()
    line = line.replace(" are ", " is ")
    line = line.replace(" black and white ", " black white ")
    line = line.replace(" brown and white ", " brown white ")
    line = line.replace("the limit of your vision is ", "the limit of your vision:")
    line = line.replace(" and ", ", ")
    line = line.replace(" is ", ", ")

    return line


def get_quantity(token: str) -> int:
    return


def run_parser(lines: list[str]):
    # The output from tt++ is always a single line
    line = lines[0]
    mdt_line = handle_tintin_array(line)

    # Initial replacements
    mdt_line = run_initial_replacements(mdt_line)

    # Tokenize
    mdt_tokens = mdt_line.split(", ")
    context = Context()

    room_results = []

    for token in mdt_tokens:
        if len(token) > 0 and ' of a ' not in token:
            context.ignoring_exits = token.startswith(EXIT_TOKENS)

        elif token.startswith('the limit of your vision:'):
            if context.last_count > 0:
                this_room = [context.last_count, context.last_direction, context.room_id, int(math.floor(context.room_value))]
                context.nothing = False
                context.next_color = ""
                context.room_id = context.room_id + 1
                context.room_value = 0
            
            context.last_direction = ""
            context.last_enemy_line = ""
            context.last_count = 0
            context.last_was_dir = 0

        else:
            quantity = ""


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


    return


def watch_files(filename: str):
    last_update_time = os.stat(filename).st_mtime

    with open(filename, "r") as f:
        while True:
            new_time = os.stat(filename).st_mtime
            
            # If the files modified time has changed, run the parser
            if new_time != last_update_time:
                last_update_time = new_time
                run_parser(f.readlines())
                f.seek(0)

            time.sleep(0.2)

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
