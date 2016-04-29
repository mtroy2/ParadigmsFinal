
import sys
import os
import pygame
from pygame.locals import *

from GameObjects import Walls
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
		self.laserID = 2
		self.size = self.width,self.height = 455,500
		self.screen = pygame.display.set_mode(self.size)

		#7
		self.black = 0,0,0
		self.screen.fill(self.black)


		# initialize game objects
		self.gameObjects = []
		self.player1 = Player1()
		self.walls = Walls()
		self.gameObjects.append(self.walls)
		self.gameObjects.append(self.player1)
		self.screen.blit(self.walls.image,self.walls.image.get_rect())


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
				self.inputState["click"] = False

		
	
		
		for item in self.gameObjects:
			self.screen.blit(item.image, item.rect)
	
		#pygame.display.flip()


	def deleteObject(self,objectID):
		# look for object in game objects, if found, remove from list
		index = 0
		found = False
		for item in self.gameObjects:
			if item.ID == objectID:
				found = True
				break
			index += 1	
		if found:
			del(self.gameObjects[index])
	
	# handle enemy explode sound		
	#def init_game_objects(self):
	#	ss = spritesheet.spritesheet(os.getcwd() + "/tiles/sprites.png")
	#	game_map = pygame.transform.scale2x(ss.image_at((226,0,235,248)))
	#	block = pygame.transform.scale2x(ss.image_at((9,10,5,5)))
		
	#	pacman = ss.image_at((457,0,10,15))
	#	power_boost = pygame.transform.scale2x(ss.image_at((8,24,8,8)))
	#	self.screen.blit(game_map,game_map.get_rect())

	#	pygame.display.flip()

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
	#reactor.run()
	#reactor.run()
	while 1:
		continue
	lc.stop
