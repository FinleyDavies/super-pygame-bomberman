# content to include in message:
# message length, what type of message
# if type is 0 then command message:
# command id, command arguments


# client out job:
# send contents of game commands queue every frame, if nothing, do not send
# when requested, send copies of game objects to compare with the server
# when requested, respond to a ping from server to determine latency

# client in job:
# receive game commands in serialized format and decode, adding them to commands queue
# receive ping and get game state requests accordingly


# server out job:
# send all game updates to every client
# send game state requests at regular intervals to every client
# send ping requests to every client at regular intervals

# server in job:
# receive game commands from all clients and add to server queue
# receive game states from each client and compare them to server state
# receive ping replies from the client and store latency


# server threads:
# client thread to run for each connection

import threading

class SocketServer(threading.Thread):
	def __init__(self):
		# initialise server socket and bind to specified port and address
		pass

	def run(self):
		pass
