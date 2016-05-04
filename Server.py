# Server.py
# Server class to handle connections to two players and send game states
# back and forth

import cPickle as pickle
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from GameSpace import GameSpace
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
		print "Num connections = ", self.factory.num_connections
		if self.factory.num_connections == 1 or self.factory.num_connections == 2:
			self.state = AUTHENTICATING
		else:
			self.state = EXIT_GAME

	def lookupBinding(self,keyEntered):
		for binding,keyBound in self.bindings.items():
			if keyEntered == keyBound:
				
				return binding
		return "not found"

	def lineReceived(self, line):
		if self.state == AUTHENTICATING:
			self.factory.users[line] = self
			data = {}
			if self.factory.num_connections == 1:
				data["type"] = "GOTO_WAITING"
			else:
				data["type"] = "GOTO_PLAYING"
				data["obstacles"] = []
				for obstacle in gs.game_obstacles:
					data["obstacles"].append(obstacle.rect.center)
				self.state = PLAYING

			data = pickle.dumps(data)
			for name,protocol in self.factory.users.iteritems():
				protocol.sendLine(data)
		else:
			make_bullet = False
			line = pickle.loads(line)
			p = line["player"]
			inputState = line["inputState"]
			mpos = line["mouse"]
		
			# Tank movement
			for event, status in inputState.items():
				if status:
					if event == "up" or event == "down":
						self.gs.players[p].move(event)
					elif event == "left" or event == "right":
						self.gs.players[p].rotate(event)
					elif event == "click":
						print "running click"
						if self.gs.players[p].ammo > 0:
							make_bullet = True
						self.gs.players[p].click()
						
			# Tick player
			self.gs.players[p].tick(mpos[0], mpos[1])

			# Update the game state
			self.updateGameState(make_bullet)

	
	def connectionLost(self, reason):
		print 'connection from', self.addr, 'lost:', reason
		print 'Player left the game, booting remaining players'
		self.state = AUTHENTICATING
		data = {}
		data["type"] = "GOTO_MENU"
		data = pickle.dumps(data)
		for name, protocol in self.factory.users.iteritems():
			protocol.sendLine(data)
		self.factory.num_connections = 0
		self.factory.users.clear()
		self.gs.reset()


	def updateGameState(self,make_bullet):
		# Each player gets +1 ammo every 5 seconds
		self.gs.ammo_increase_counter += 1./60
		if self.gs.ammo_increase_counter >= 10.0:
			self.gs.ammo_increase_counter = 0.
			self.gs.players[0].increase_ammo(1)
			self.gs.players[1].increase_ammo(1)

		data = {}
		data["bullets"] = []
		# Tick bullets
		for bullet in self.gs.bullets:
			bullet.tick()
			bullet_dict = {}
			bullet_dict["center"] = bullet.center
			bullet_dict["angle"] = bullet.angle
			data["bullets"].append( bullet_dict )

		data["make_bullet"] = make_bullet
		data["type"] = "UPDATE"
		data["player1"] = {}
		data["player1"]["rect_center"] = self.gs.players[0].rect.center
		data["player1"]["angle"] = self.gs.players[0].angle
		data["player1"]["health"] = self.gs.players[0].health
		data["player1"]["ammo"] = self.gs.players[0].ammo
		data["player1"]["turret_center"] = self.gs.players[0].turret.rect.center
		data["player1"]["turret_angle"] = self.gs.players[0].turret.angle
		data["player2"] = {}
		data["player2"]["rect_center"] = self.gs.players[1].rect.center
		data["player2"]["angle"] = self.gs.players[1].angle
		data["player2"]["health"] = self.gs.players[1].health
		data["player2"]["ammo"] = self.gs.players[1].ammo
		data["player2"]["turret_center"] = self.gs.players[1].turret.rect.center
		data["player2"]["turret_angle"] = self.gs.players[1].turret.angle

		if data["player1"]["health"] <= 0 or data["player2"]["health"] <= 0:
			self.gs.reset()

		data = pickle.dumps(data)
		for name, protocol in self.factory.users.iteritems():
			protocol.sendLine(data)

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
