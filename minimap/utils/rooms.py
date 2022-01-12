from maps import *

class Room:
    def __init__(self, exits):
        self.exits = exits
        self.description = ""
    

class RoomMap:
    def __init__(self, map: list[list]):
        self.rooms: list[Room] = []

        self.rows = len(map)
        self.cols = len(map[0])

        self.buildRoomMap(map) 


    def getRoom(self, x: int, y: int) -> Room:
        return self.rooms[y * self.cols + x]


    def buildRoomMap(self, map: list[list]):
        for y in range(self.rows):
            for x in range(self.cols):
                self.rooms.append(Room(getExits(y, x, map)))
