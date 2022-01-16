import phxsocket
import json
import time
import os

# read username from follows.json
with open('follows.json', 'r') as f:
    follows = json.load(f)
    username = follows['username']

    socket = phxsocket.Client("ws://localhost:4000/socket/websocket", {"params": {"token": None}})

    if socket.connect(): # blocking, raises exception on failure
      topic = "user_map:{}".format(username)
      channel = socket.channel(topic, {})
      resp = channel.join() # also blocking, raises exception on failure

      socket.on_close = lambda socket: socket.connect()

      follows_filename = "../logs/map.log"
      # create file if doesn't exist
      if not os.path.exists(follows_filename):
        open(follows_filename, 'w').close()
        
      look_filename = "../logs/look.log"
      # create file if doesn't exist
      if not os.path.exists(look_filename):
        open(look_filename, 'w').close()
      
      follows_cached_stamp = os.stat(follows_filename).st_mtime
      look_cached_stamp = os.stat(look_filename).st_mtime
      while True:
        # monitor follows
        time.sleep(0.1)
        follows_stamp = os.stat(follows_filename).st_mtime
        if follows_stamp != follows_cached_stamp:
            with open(follows_filename, 'r') as f:
                line = f.readline().rstrip()
                channel.push("mud_msg", {"body": {"direction": line, "username": username}})
                follows_cached_stamp = follows_stamp
        
        # monitor look
        look_stamp = os.stat(look_filename).st_mtime
        if look_stamp != look_cached_stamp:
            with open(look_filename, 'r') as f:
                line = f.readline().rstrip()
                channel.push("mud_msg", {"body": {"room_short": line, "username": username}})
                look_cached_stamp = look_stamp
