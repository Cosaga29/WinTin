from utils.rooms import *
from utils.maps import *

map_dir = "/home/alex/mud/minimap/maps"

# TODO:
#def build(self, tilemaps: dict):
#    for name, map in tilemaps.items():
#        roommap = RoomMap(map)
#
#        print(roommap.getRoom(4, 2).exits)


def main():
    map = TilemapLoader(map_dir)
    map.load()
    print(map.tilemaps.keys())
    print(map.tilemaps['shades'].keys())


main()