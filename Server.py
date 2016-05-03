# Server.py
# Server class to handle connections to two players and send game states
# back and forth

import cPickle as pickle
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from PyGame import GameSpace
from GameConstants import *
SERVER_PORT = 9000

class ServerConn(LineReceiver):
	def __init__(self, addr, game_state,factory):
		self.addr = addr
		#This is the main game state
		self.gs = game_state
		# Factory that generates this object - used for persistent variable tracking
		self.factory = factory
		# variables shared across all server connections
		self.users = self.factory.users
		self.state = self.factory.state
		self.num_connections = self.factory.num_connections
	def connectionMade(self):
		self.factory.num_connections += 1

		if self.factory.num_connections == 1 or self.factory.num_connections == 2:
			self.state = AUTHENTICATING
		else:
			self.state = EXIT_GAME


	def lineReceived(self, line):


		if self.state == AUTHENTICATING:
			self.users[line] = self
			if self.factory.num_connections == 1:
				message = "GOTO_WAITING"
			else:
				message = "GOTO_PLAYING"
				self.state = PLAYING

			for name,protocol in self.users.iteritems():
				protocol.sendLine(message)
		else:
			pass


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
		self.state = WAITING_2
	def buildProtocol(self, addr):
		return ServerConn(addr, self.gs,self)


if __name__ == '__main__':
	gs = GameSpace()

	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
