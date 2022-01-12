import os
import json
from os import path
from enum import Enum
import re


class Tile(Enum):
    BLANK = 1
    ROOM = 2
    EXIT = 3


def inBounds(x, y, max_x, max_y) -> bool:
    return x >= 0 and y >= 0 and x < max_x and y < max_y


def isLinked(x1, y1, x2, y2, map) -> bool:
    if inBounds(x1, y1, len(map[0]), len(map)) and inBounds(x2, y2, len(map[0]), len(map)):
        return map[y1][x1] == Tile.ROOM and map[y2][x2] == Tile.ROOM


def getExits(y, x, map):
    exits = []

    # Check Upper Left
    dir = (x-1, y-1)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("nw")

    # Check Up
    dir = (x, y-1)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("n")

    # Check Upper Right
    dir = (x+1, y-1)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("ne")

    # Check Left
    dir = (x-1, y)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("w")

    # Check Right
    dir = (x+1, y)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("e")

    # Check Bottom Left
    dir = (x-1, y+1)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("sw")

    # Check Bottom
    dir = (x, y+1)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("s")

    # Check Bottom Right
    dir = (x+1, y+1)
    if isLinked(x, y, dir[0], dir[1], map):
        exits.append("se")

    return exits


class TilemapLoader:
    def __init__(self, map_dir):
        self.map_dir = map_dir

        # Tilemaps can be accessed by name i.e. shades.mappings / shades.map
        # will be stored as a key, 'shades' in tilemaps.
        #
        # A tilemap currently consists of a dictionary containing 'data' and 'mappings' keys
        # 'data' corresponds to the map file data, 'mappings' is the loaded JSON 
        self.tilemaps = {}


    def getTileValue(self, tile):
        if tile == '-':
            return Tile.BLANK
        elif tile == 'O':
            return Tile.ROOM
        else:
            return Tile.EXIT


    def getmap(self, map_name):
        if map_name in self.tilemaps:
            return self.tilemaps[map_name]


    def load(self):
        files = os.listdir(self.map_dir)
        print(files)

        for file in files:
            if re.search(r'.map$', file):
                print(file)
                filename_base = file.replace('.map', '')

                with open(path.join(self.map_dir, file)) as f:
                    rows = []
                    for line in f.readlines():
                        line = line.rstrip()
                        row = []
                        if line:
                            for char in line:
                                row.append(self.getTileValue(char))
                            rows.append(row)
                self.tilemaps[filename_base] = {}
                self.tilemaps[filename_base]['data'] = rows

                mapping_file = filename_base + ".mappings"

                if mapping_file in files:
                    with open(path.join(self.map_dir, mapping_file)) as m:
                        self.tilemaps[filename_base]['mappings'] = json.load(m)
                #Example print(self.maps['smugs.map'][0]) -> get smugs map
