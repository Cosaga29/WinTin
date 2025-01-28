import re
from enum import Enum

from definitions import (
    RoomInfo,
    EntityInfo,
    NUMBER_MAP,
    DIRECTION_MAP,
    IGNORE_TOKENS,
)
from patterns import PLAYER_COLOR
from config import MdtColors


def filter_exits(lines: list[str]) -> list[str]:
    num_lines = len(lines)
    to_return = []
    current_idx = 0
    while current_idx < num_lines:
        line = lines[current_idx]
        if line.startswith(IGNORE_TOKENS):
            follow_on_direction = True

            # If line starts with any of these, remove it and any follow on directions...
            while follow_on_direction and current_idx + 1 < num_lines:
                next_line = lines[current_idx + 1]
                words = next_line.split(" ")
                if len(words) == 1 and words[0] in DIRECTION_MAP:
                    current_idx += 1
                elif (
                    len(words) >= 2
                    and words[0] in NUMBER_MAP
                    and words[1] in DIRECTION_MAP
                ):
                    current_idx += 1
                else:
                    follow_on_direction = False
        else:
            to_return.append(line)

        current_idx += 1

    return to_return


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


class MdtContextParser:
    class State(Enum):
        DONE = 1
        ADD_ENTITIES = 2
        ADD_DIRECTIONS = 3
        EVAL_TOKEN = 4
        ADD_ENTITIES_AND_DIRECTIONS = 5
        GET_TOKEN = 6

    def __init__(self, line: str):
        self.tokens = self._precondition_lines(line)

        # Precompute this now for reuse
        self.word_tokens = list(map(lambda x: x.split(" "), self.tokens))

        self.num_tokens = len(self.tokens)
        self.token_idx = 0
        self.token: str = ""

        self.state = MdtContextParser.State.DONE
        self.mdt_rooms: dict[tuple[tuple[int, str]], RoomInfo] = {}

        self.entity_stack = []
        self.direction_stack = []

        self.entities = ""
        self.directions = ""

        self.state_executor = {
            MdtContextParser.State.GET_TOKEN: self.get_next_token,
            MdtContextParser.State.EVAL_TOKEN: self.evaluate_token,
            MdtContextParser.State.ADD_ENTITIES: self.add_entities,
            MdtContextParser.State.ADD_DIRECTIONS: self.add_directions,
            MdtContextParser.State.ADD_ENTITIES_AND_DIRECTIONS: self.parse_entities_and_dir,
        }

    def _precondition_lines(self, line: str):
        # Convert everything to lowercase for matching purposes
        line = line.lower()

        # Helps with tokenizing entities and directions
        # 'two hops are southeast' is logically equivalent to 'two hops is southeast', just bad english
        line = line.replace("are", "is")

        # TODO: Determine if this one is safe to tokenize
        line = line.replace(
            "and the limit of your vision", ", the limit of your vision"
        )

        # Commas are the main tokens that can be used to identify room elements
        lines = line.split(", ")

        # Remove room entries that we don't care about (along with their directions!)
        lines = filter_exits(lines)

        return lines

    def read(self) -> dict[tuple[tuple[int, str]], RoomInfo]:
        self.state = MdtContextParser.State.GET_TOKEN
        while self.state != MdtContextParser.State.DONE:
            self.state_executor[self.state]()

        if len(self.entity_stack) > 0 and len(self.direction_stack) > 0:
            self.push_room()

        return self.mdt_rooms

    def get_next_token(self):
        if self.token_idx < self.num_tokens:
            self.token = self.tokens[self.token_idx].rstrip().lstrip()
            self.state = MdtContextParser.State.EVAL_TOKEN
        else:
            self.state = MdtContextParser.State.DONE

    def evaluate_token(self):
        fragments = self.token.split(" is ")
        directions = None if len(fragments) < 2 else fragments[1]

        # 'neelie awkside and a sailor is one southwest'
        if directions is not None:
            self.entities = fragments[0]
            self.directions = fragments[1]
            self.state = MdtContextParser.State.ADD_ENTITIES_AND_DIRECTIONS
        else:
            words = self.word_tokens[self.token_idx]
            if len(words) < 2:
                # Has to be a named NPC or Player
                self.entities = fragments[0]
                self.state = MdtContextParser.State.ADD_ENTITIES
                return
            
            # Skip this token
            if words[0] in DIRECTION_MAP:
                self.token_idx += 1
                self.state = MdtContextParser.State.GET_TOKEN
                return

            # one south and one east
            if words[0] in NUMBER_MAP and words[1] in DIRECTION_MAP:
                # Directions only make sense if we have entities to relate them too
                if len(self.entity_stack) > 0:
                    self.directions = fragments[0]
                    self.state = MdtContextParser.State.ADD_DIRECTIONS
                else:
                    self.token_idx += 1
                    self.state = MdtContextParser.State.GET_TOKEN
                return
            else:
                # Has to be an entity
                self.entities = fragments[0]
                self.state = MdtContextParser.State.ADD_ENTITIES
                return

    def add_entities(self):
        # If we have directions in the stack, we have the start of a new room definition..
        if len(self.direction_stack) > 0:
            self.push_room()

        push_entities(self.entities, self.entity_stack)
        self.state = MdtContextParser.State.GET_TOKEN
        self.token_idx += 1

    def add_directions(self):
        push_directions(self.directions, self.direction_stack)
        # Last direction detected
        if len(self.entity_stack) > 0 and "and" in self.directions:
            self.push_room()

        self.state = MdtContextParser.State.GET_TOKEN
        self.token_idx += 1

    def parse_entities_and_dir(self):
        # If we have directions in the stack, we have the start of a new room definition..
        if len(self.direction_stack) > 0:
            self.push_room()

        push_entities(self.entities, self.entity_stack)
        push_directions(self.directions, self.direction_stack)
        # Last direction detected
        if len(self.entity_stack) > 0 and "and" in self.directions:
            self.push_room()

        self.token_idx += 1
        self.state = MdtContextParser.State.GET_TOKEN

    def push_room(self):
        room = RoomInfo()
        room.entities.extend(self.entity_stack)
        self.mdt_rooms[tuple(self.direction_stack)] = room
        self.direction_stack.clear()
        self.entity_stack.clear()
