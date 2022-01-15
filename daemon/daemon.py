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

  def respond(payload):
      # do nothing

  filename = "../logs/follows.log"
  # create file if doesn't exist
  if not os.path.exists(filename):
    open(filename, 'w').close()

  cached_stamp = os.stat(filename).st_mtime
  # get first line from ../logs/follows.log
  while True:
    time.sleep(0.1)
    stamp = os.stat(filename).st_mtime
    if stamp != cached_stamp:
        with open(filename, 'r') as f:
            line = f.readline().rstrip()
            channel.push("mud_msg", {"body": {"room_short": line}}, respond)
            cached_stamp = stamp