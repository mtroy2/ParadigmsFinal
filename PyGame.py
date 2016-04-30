
import sys
import os
import pygame
from pygame.locals import *

from GameObjects import *
import math
import spritesheet
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.tcp import Port
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.protocol import ClientFactory
import os
import random
#Set up variables for host and port to connect to
SERVER_HOST = 'student01.cse.nd.edu'
SERVER_PORT = 40093
COMMAND_PORT = 32010
DATA_PORT = 32011
CLIENT_PORT = 8888

class GameSpace:
	def __init__(self):
		# init game
		# dict of key_pressed to SDL event triggered
		self.bindings = {"up": pygame.K_UP,
						"down": pygame.K_DOWN,
						"right": pygame.K_RIGHT,
						"left": pygame.K_LEFT,
						"click": pygame.MOUSEBUTTONDOWN}
		# Dict of key to its curernt state
		self.inputState = {"up": False,
						"down": False,
						"right": False,
						"left": False,
						"click": False}
		
		pygame.init()   
		# Each game object has a unique ID, Player and Enemy start at 0 and 1, respectively
		
		self.bulletID = 1
		self.size = self.width,self.height = 455,475
		self.screen = pygame.display.set_mode(self.size)
		self.map = Map(self)
		#7
		



		# initialize game objects
		self.game_objects = []
		self.game_obstacles=[]
		self.bullets = []
		self.players = []
		self.turret1 = Turret((66,29,6,23),self)
		self.turret2 = Turret((66,80,6,23),self)
		self.player1 = Tank(self.turret1, "PLAYER_1",(50,50),self)
		self.player2 = Tank(self.turret2, "PLAYER_2", (400,400),self)
		self.walls = Walls(self)
		#self.gameObjects.append(self.walls)
		self.players.append(self.player1)
		self.players.append(self.player2)
		self.screen.blit(self.map.image,self.map.rect)
		self.create_obstacles()
		pygame.display.flip()

	# given a key, lookup the event for it	
	def lookupBinding(self,keyEntered):
		for binding,keyBound in self.bindings.items():
			if keyEntered == keyBound:
				return binding
		return "not found"


	def main(self):
		
		#5 user input reading from queue
		for event in pygame.event.get():
			#exit if X is pressed
			if event.type == QUIT:
				sys.exit()
			# if any key is pressed, look it up,
			# if it is one of the mapped keys, make its pressed status true
			if event.type == KEYDOWN:
				binding = self.lookupBinding(event.key)
				if binding != "not found":
					self.inputState[binding] = True
			# If any key is released, and it is mapped, make its pressed status false		
			if event.type == KEYUP:
				binding = self.lookupBinding(event.key)
				if binding != "not found":
					self.inputState[binding] = False
			# if mouse is pressed		
			if event.type == MOUSEBUTTONDOWN:
				#set click status to True
				self.inputState["click"] = True

				
			if event.type == MOUSEBUTTONUP:	
				self.players[0].click()
		#6 tick updating
		for event, status in self.inputState.items():
			# loop through dict, if the status of that button is True (pressed)
			if status:
				# on click, run click function in player
				if event == "up" or event == "down":
					# otherwise, it's a movement. Run move function
					self.players[0].move(event)
				elif event == "left" or event == "right":
					self.players[0].rotate(event)
		
		# redraw map
		self.screen.blit(self.map.image, self.map.rect)
		#redraw bushes
		for bush in self.game_obstacles:
			self.screen.blit(bush.image, bush.rect)

		for player in self.players:
			player.tick()
			self.screen.blit(player.image, player.rect)
			self.screen.blit(player.turret.image, player.turret.rect)
		for bullet in self.bullets:
			bullet.tick()
			self.screen.blit(bullet.image,bullet.rect)
		pygame.display.flip()


	def delete_bullet(self,objectID):
		# look for object in game objects, if found, remove from list
		index = 0
		found = False
		for item in self.bullets:
			if item.ID == objectID:
				found = True
				break
			index += 1	
		if found:
			del(self.bullets[index])
	
	# handle enemy explode sound		
	#def init_game_objects(self):
	#	ss = spritesheet.spritesheet(os.getcwd() + "/tiles/sprites.png")
	#	game_map = pygame.transform.scale2x(ss.image_at((226,0,235,248)))
	#	block = pygame.transform.scale2x(ss.image_at((9,10,5,5)))
		
	#	pacman = ss.image_at((457,0,10,15))
	#	power_boost = pygame.transform.scale2x(ss.image_at((8,24,8,8)))
	#	self.screen.blit(game_map,game_map.get_rect())

	#	pygame.display.flip()
	def create_obstacles(self):
		
		for i in range(0,6):
			rand_x = random.randint(50,380)
			rand_y = random.randint(50,380)
			rand_type = random.randint(1,2)
			if (rand_x <= 90 and rand_x >=15 and rand_y <=90 and rand_y >= 15) :
				rand_x = random.randint(50,380)
				rand_y = random.randint(50,380)
			elif (rand_x <= 400 and rand_x >= 350 and rand_y <= 450 and rand_y >= 360):
				rand_x = random.randint(50,380)
				rand_y = random.randint(50,380)
			obstacle = Obstacle((rand_x,rand_y),rand_type)
			self.screen.blit(obstacle.image,obstacle.rect)
			self.game_obstacles.append(obstacle)
	def create_bullet(self, center, angle):
		bullet = Bullet(center, angle, self.bulletID, self)
		self.bullets.append(bullet)
		# update id
		self.bulletID += 1	
class WorkHomeReceiver(LineReceiver):
	def __init__(self,addr):
		"""Constructor for Server running, servicing work connections on home machine"""

		self.addr = addr
		print "Work<-->Home: Command Connection received from work: "

	def connectionMade(self):
		"""This runs after the connection is verified on both sides"""

		print "Work<-->Home: Command Connection established"
		############
		print "Listening on ", CLIENT_PORT
		#reactor.listenTCP(CLIENT_PORT, ClientHomeFactory(self))
		#newListen(CLIENT_PORT,self)

	def sendData(self,data):
		self.transport.write(data)

	def error(self,message):
		self.transport.write(message)

	def connectionLost(self,reason):
		print "Work<-->Home: Lost command connection to work computer "
		


class WorkHomeFactory(Factory):
	"""This is a class that builds the server to handle connections from the client"""
	def buildProtocol(self,addr):
		return WorkHomeReceiver(addr)


if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.main)
	lc.start(1/60)

	#reactor.listenTCP(COMMAND_PORT, WorkHomeFactory())
	reactor.run()
	#reactor.run()
	lc.stop
