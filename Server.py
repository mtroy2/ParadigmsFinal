# Server.py
# Server class to handle connections to two players and send game states
# back and forth

import cPickle as pickle
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from PyGame import GameSpace
from GameConstants import *
SERVER_PORT = 9000

class ServerConn(Protocol):
	def __init__(self, addr, game_state, num_cons, users):
		self.addr = addr
		self.gs = game_state
		self.num_conns = num_cons
		self.users = users



	def connectionMade(self):
		print 'new connection from', self.addr
		self.num_conns += 1
		print "Number of active connections = " +str(self.num_conns)
		if self.num_conns == 1:
			line = "GOTO_WAITING_1" + "\n"
			self.transport.write(line)
		else:
			line = "GOTO_INFO"
			self.transport.write(line)

	def dataReceived(self, data):
		info = pickle.loads(data)
		self.gs.dq.push(info)

	def connectionLost(self, reason):
		print 'connection from', self.addr, 'lost:', reason
		print 'Player left the game, waiting for new player'


	def updateGameState(self, player_info, bullet_info):
		data = {}
		# data["contents"] = player_X_info:
		#	"rect_center" 	= self.gs.players[X].rect.center
		#	"angle"			= self.gs.players[X].angle
		# 	"health"		= self.gs.players[X].health
		# 	"ammo"			= self.gs.players[X].ammo
		#	"turret_angle"  = self.gs.players[X].turret.angle
		# data["contents"] = bullet_info:
		#	"bullets"		= [list of dicts]:
		#						"center" 	= bullet.center
		#						"angle"		= bullet.angle
		#						"dist"		= bullet.total_distance
		#						

class ServerConnFactory(Factory):
	def __init__(self, gamestate):
		self.num_connections = 0
		self.users = {} # maps user names to Chat instances
		self.gs = gamestate

	def buildProtocol(self, addr):
		return ServerConn(addr, self.gs, self.num_connections, self.users)


if __name__ == '__main__':
	gs = GameSpace()

	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
