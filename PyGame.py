
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
#Set up variables for host and port to connect to
SERVER_HOST = 'student01.cse.nd.edu'
SERVER_PORT = 40093
COMMAND_PORT = 32010
DATA_PORT = 32011
CLIENT_PORT = 8888
TITLE_SCREEN = 0
WAITING_2 = 1
WAITING_1 = 2
INFO_SCREEN = 3
WAITING_FOR_PLAYER = 4
PLAYING = 5
PLAYER_1_DEAD = 6
PLAYER_2_DEAD = 7

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
		self.font = pygame.font.SysFont("monospace",15)
		self.bulletID = 1
		self.size = self.width,self.height = 500,700
		self.screen = pygame.display.set_mode(self.size)
		self.map = Map(self)
		#7
		self.state = WAITING_2

		self.info_screen = Info_screen(self)
		self.title_screen = Title_screen(self)
		self.win_screen = Win_screen(self)
		# initialize game objects
		self.game_objects = []
		self.game_obstacles=[]
		self.bullets = []
		self.players = []
		self.turret1 = Turret("PLAYER_1",self)
		self.turret2 = Turret("PLAYER_2",self)
		self.player1 = Tank(self.turret1, "PLAYER_1",(50,150),self)
		self.player2 = Tank(self.turret2, "PLAYER_2", (400,500),self)
		self.walls = Walls(self)
		#self.gameObjects.append(self.walls)
		self.players.append(self.player1)
		self.players.append(self.player2)
		self.create_obstacles()

		self.waiting_text_state = 1
		self.waiting_counter = 0.0
		self.ammo_increase_counter = 0.0
		self.waiting_text_1 = self.font.render("Waiting for other player.",1,(255,255,255))
		self.waiting_text_2 = self.font.render("Waiting for other player..",1,(255,255,255))
		self.waiting_text_3 = self.font.render("Waiting for other player...",1,(255,255,255))
		self.p1_win_text = self.font.render("PLAYER 1 WINS!",1,(255,255,255))
		self.p2_win_text = self.font.render("PLAYER 2 WINS!",1,(255,255,255))
	# given a key, lookup the event for it	
	def lookupBinding(self,keyEntered):
		for binding,keyBound in self.bindings.items():
			if keyEntered == keyBound:
				return binding
		return "not found"


	def main(self):
	
		if self.state == TITLE_SCREEN or self.state == WAITING_1 or self.state == WAITING_2:
			self.title_menu()
			pygame.display.flip()

		elif self.state == INFO_SCREEN:
			self.info_menu()
			pygame.display.flip()
		elif self.state == PLAYING:
			self.active_game()

		elif self.state == PLAYER_1_DEAD or self.state == PLAYER_2_DEAD:
			self.win_menu()
			pygame.display.flip()

	def win_menu(self):
	
		if self.win_screen.current_state == False:
			self.screen.fill((0,0,0))
			self.win_screen.current_state = True
			self.screen.blit(self.win_screen.image, self.win_screen.rect)
			if self.state == PLAYER_1_DEAD:
				self.screen.blit(self.p2_win_text, (20,37))
			else:
				self.screen.blit(self.p1_win_text, (20,37))
		for event in pygame.event.get():
			if event.type == QUIT:
				self.state = WAITING_2
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.win_screen.click((mx,my))
	def info_menu(self):
		if self.info_screen.current_state == False:
			self.info_screen.current_state = True
			self.screen.blit(self.info_screen.image,self.info_screen.rect)
		for event in pygame.event.get():	
			if event.type == QUIT:
				sys.exit()
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.info_screen.click((mx,my))
	def title_menu(self):
		self.screen.fill((0,0,0))
		self.screen.blit(self.title_screen.image,self.title_screen.rect)
		if self.state == WAITING_1:
			self.waiting_counter += 1./60
			if self.waiting_counter >= 0.5:
				self.waiting_counter = 0
				self.waiting_text_state += 1
				if self.waiting_text_state ==4:
					self.waiting_text_state = 1
			if self.waiting_text_state == 1:
				self.screen.blit(self.waiting_text_1,(150,270))
			elif self.waiting_text_state == 2:
				self.screen.blit(self.waiting_text_2,(150,270))
			elif self.waiting_text_state == 3:
				self.screen.blit(self.waiting_text_3,(150,270))
	
	

		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.title_screen.click((mx,my))
	def active_game(self):
		#5 user input reading from queue
		self.ammo_increase_counter += 1./60
		if self.ammo_increase_counter >= 10.0:
			self.ammo_increase_counter = 0.
			self.players[0].increase_ammo(1)
			self.players[1].increase_ammo(1)
			self.show_ammo()
		for event in pygame.event.get():
			#exit if X is pressed
			if event.type == QUIT:
				sys.exit()
			# if anyile "PyGame.py", line 9 key is pressed, look it up,
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
				self.show_ammo()
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
		self.screen.fill((0,0,0))
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
		self.draw_health_bars()	
		self.show_ammo()
		# Draw bounding boxes
		#pygame.draw.polygon(self.screen,(0,0,0),[self.players[0].rect.topleft,
		#	self.players[0].rect.topright,self.players[0].rect.bottomright,self.players[0].rect.bottomleft], 1)
		pygame.display.flip()



	def draw_health_bars(self):
		pygame.draw.rect(self.screen,(255,0,0),(102,36,self.players[0].health,14))
		pygame.draw.rect(self.screen,(255,0,0),(345,36,self.players[1].health,14))
	def show_ammo(self):
		player_1_ammo = self.font.render(str(self.players[0].ammo),1,(255,255,255))
		player_2_ammo = self.font.render(str(self.players[1].ammo),1,(255,255,255))
		self.screen.blit(player_1_ammo, (85,64))
		self.screen.blit(player_2_ammo, (332,63))
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
			obstacle = Obstacle((rand_x,rand_y),rand_type)
			self.game_obstacles.append(obstacle)

	def create_bullet(self, center, angle):
		# calculate initial point of bullet
		dy =  math.sin(angle) * 26
		dx = math.cos(angle) * 26
		new_center = (center[0]+ dx,center[1]-dy)
		bullet = Bullet(new_center, angle, self.bulletID, self)
		self.bullets.append(bullet)
		# update id
		self.bulletID += 1	

	def reset(self):
		del self.game_objects[:]
		del self.game_obstacles[:]
		del self.bullets[:]
		del self.players[:]
		self.bulletID = 1
		self.turret1 = Turret("PLAYER_1",self)
		self.turret2 = Turret("PLAYER_2",self)
		self.player1 = Tank(self.turret1, "PLAYER_1",(50,150),self)
		self.player2 = Tank(self.turret2, "PLAYER_2", (400,500),self)
		self.walls = Walls(self)
		#self.gameObjects.append(self.walls)
		self.players.append(self.player1)
		self.players.append(self.player2)
		self.create_obstacles()

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
	lc.stop()
