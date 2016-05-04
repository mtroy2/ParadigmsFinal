
import sys
import os
import pygame
from pygame.locals import *

from GameObjects import *
from GameScreens import *
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
import random
from GameConstants import *
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
		# Dict of key to its current state
		self.inputState = {"up": False,
						"down": False,
						"right": False,
						"left": False,
						"click": False}

		self.bulletID = 1
		self.size = self.width,self.height = 500,700
		self.screen = pygame.display.set_mode(self.size)
		self.map = Map(self)

		# initialize game objects
		self.game_obstacles=[]
		self.bullets = []
		self.players = []
		self.turret1 = Turret("PLAYER_1",self)
		self.turret2 = Turret("PLAYER_2",self)
		self.player1 = Tank(self.turret1, "PLAYER_1",(50,150),self)
		self.player2 = Tank(self.turret2, "PLAYER_2", (450,500),self)

		self.players.append(self.player1)
		self.players.append(self.player2)
		# make all bushes on screen
		self.create_obstacles()

		# game counters

		self.ammo_increase_counter = 0.0
		
		pygame.init()   

	# given a key, lookup the event for it	
	def lookupBinding(self,keyEntered):
		for binding,keyBound in self.bindings.items():
			if keyEntered == keyBound:
				
				return binding
		return "not found"


	def active_game(self):
		if self.context == "server":
			# Each player gets +1 ammo every 5 seconds
			self.ammo_increase_counter += 1./30
			if self.ammo_increase_counter >= 10.0:
				self.ammo_increase_counter = 0.
				self.players[0].increase_ammo(1)
				self.players[1].increase_ammo(1)
				self.show_ammo()

			# Pull events off DeferredQueue and process
			obj = self.dq.get()
			while obj:
				player = obj["player"]
				event = obj["event"]
				#exit if X is pressed
				if event.type == QUIT:
					sys.exit()
		

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


				# on click , fire		
				if event.type == MOUSEBUTTONUP:	
					self.players[player-1].click()
					self.show_ammo()

			# Handle tank mvt
			for event, status in self.inputState.items():
				# loop through dict, if the status of that button is True (pressed)
				if status:
					# on click, run click function in player
					if event == "up" or event == "down":
						# otherwise, it's a movement. Run move function
						self.players[player-1].move(event)
					elif event == "left" or event == "right":
						self.players[player-1].rotate(event)

			# Redraw all objects on screen
			self.screen.fill((0,0,0))
			# redraw map
			self.screen.blit(self.map.image, self.map.rect)
			#redraw bushes
			for bush in self.game_obstacles:
				self.screen.blit(bush.image, bush.rect)
			# tick player, and redraw		# Players should tick themselves from client side
			for player in self.players:
				player.tick()
				self.screen.blit(player.image, player.rect)
				self.screen.blit(player.turret.image, player.turret.rect)
			#Tick bullets, and redraw		# Bullets should be ticked from server
			for bullet in self.bullets:
				bullet.tick()
				self.screen.blit(bullet.image,bullet.rect)
			# Draw ammo and health
			self.draw_health_bars()	
			self.show_ammo()

			pygame.display.flip()

		else:
			# Client: get events off pygame's queue & send to server
			for event in pygame.event.get():
				self.conn.sendEvent(event)


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
	

	def create_obstacles(self):
		#Randomly make 8 bushes, make them such that they can't box in a player in the corner
		for i in range(0,8):
			rand_x = random.randint(120,380)
			rand_y = random.randint(150,480)
			rand_type = random.randint(1,2)
			if (rand_x <= 90 and rand_x >=15 and rand_y <=90 and rand_y >= 15) :
				rand_x = random.randint(120,380)
				rand_y = random.randint(150,480)
			elif (rand_x <= 400 and rand_x >= 350 and rand_y <= 450 and rand_y >= 360):
				rand_x = random.randint(120,380)
				rand_y = random.randint(150,480)
			obstacle = Obstacle((rand_x,rand_y),1)
			self.game_obstacles.append(obstacle)

	def create_bullet(self, center, angle):
		# calculate initial point of bullet
		
		dy =  math.sin(angle) * 26 #26 is length of barrel
		dx = math.cos(angle) * 26
		new_center = (center[0]+ dx,center[1]-dy)
		bullet = Bullet(new_center, angle, self.bulletID, self)
		self.bullets.append(bullet)
		# update id
		self.bulletID += 1	

	def reset(self):
		# Reset all game objects in preparation for new game
		del self.game_obstacles[:]
		del self.bullets[:]
		del self.players[:]
		self.bulletID = 1
		self.turret1 = Turret("PLAYER_1",self)
		self.turret2 = Turret("PLAYER_2",self)
		self.player1 = Tank(self.turret1, "PLAYER_1",(50,150),self)
		self.player2 = Tank(self.turret2, "PLAYER_2", (450,500),self)
		#self.gameObjects.append(self.walls)
		self.players.append(self.player1)
		self.players.append(self.player2)
		self.create_obstacles()
		print 'reset complete'
	def connect_player(self,player):
		self.player = player

