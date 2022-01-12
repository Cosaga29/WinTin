import sqlite3

db_dir = "/home/alex/mud/minimap/database.db"

class Database:
    def __init__(self, db=db_dir):
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()

    def findRoomByDesc(self, desc):
        self.cur.execute("SELECT * FROM rooms WHERE room_short = '%s';" % desc)
        return self.cur.fetchall()