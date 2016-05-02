# Server.py
# Server class to handle connections to two players and send game states
# back and forth

import cPickle as pickle
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from PyGame import GameSpace

SERVER_PORT = 9000

class ServerConn(Protocol):
	def __init__(self, addr, gamestate, loop):
		gamestate.conns.append(self)
		self.addr = addr
		self.gs = gamestate
		self.lc = loop
		if (len(gamestate.conns) == 1):
			self.player = 1
		else:
			self.player = 2
			print 'Ready to play!'
			self.gs.state = 5 # PLAYING

	def connectionMade(self):
		print 'new connection from', self.addr

	def dataReceived(self, data):
		info = pickle.loads(data)
		self.gs.dq.push(info)

	def connectionLost(self, reason):
		print 'connection from', self.addr, 'lost:', reason
		print 'Player left the game, waiting for new player'
		self.gs.conns.remove(self)
		if (len(self.gs.conns) > 0):
			self.gs.conns[0].player = 1
		self.gs.state = 0 # TITLE_SCREEN

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
	def __init__(self, gamestate, loop):
		self.gs = gamestate
		self.lc = loop

	def buildProtocol(self, addr):
		return ServerConn(addr, self.gs, self.lc)


if __name__ == '__main__':
	gs = GameSpace("server")
	lc = LoopingCall(gs.main)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs, lc))
	reactor.run()
