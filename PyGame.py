
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
EXIT_GAME = 8
class GameSpace:
	def __init__(self, context):
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
<<<<<<< HEAD
		

		# Connection initialization
		self.context = context
		if (self.context == "server"):
			self.conns = []
		self.dq = DeferredQueue()
		

		pygame.init()

=======
		
		pygame.init()   
		self.conns = []
>>>>>>> 349a47346bfc4b9b596bbcb107ab09738ef09d75
		# font to be used for any text displayed on screen
		self.font = pygame.font.SysFont("monospace",15)

		self.bulletID = 1
		self.size = self.width,self.height = 500,700
		self.screen = pygame.display.set_mode(self.size)
		self.map = Map(self)
	
		# start state of server
		self.state = WAITING_2

		# init screens
		self.info_screen = Info_screen(self)
		self.title_screen = Title_screen(self)
		self.win_screen = Win_screen(self)

		# initialize game objects
		self.game_obstacles=[]
		self.bullets = []
		self.players = []
		self.turret1 = Turret("PLAYER_1",self)
		self.turret2 = Turret("PLAYER_2",self)
		self.player1 = Tank(self.turret1, "PLAYER_1",(50,150),self)
		self.player2 = Tank(self.turret2, "PLAYER_2", (400,500),self)

		self.players.append(self.player1)
		self.players.append(self.player2)
		# make all bushes on screen
		self.create_obstacles()

		# game counters
		self.waiting_counter = 0.0
		self.ammo_increase_counter = 0.0
	
		# Text to be displayed on screen
		self.waiting_text_state = 1
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
		# Main switches based on current state of game
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
		else:
			pygame.quit()
	
	def title_menu(self):
		#Black background
		self.screen.fill((0,0,0))
		# Load image
		self.screen.blit(self.title_screen.image,self.title_screen.rect)

		# Switch behaviour based on state
		if self.state == WAITING_1:

			# Animate Waiting message (either "Waiting for other player." "Waiting for other player.." or "Waiting of other player...")
			self.waiting_counter += 1./60
			if self.waiting_counter >= 0.5:
				self.waiting_counter = 0
				self.waiting_text_state += 1
				if self.waiting_text_state ==4:
					self.waiting_text_state = 1
			#Display appropriate message
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
				# run pass in location to title_screen object - run click method
				mx,my = pygame.mouse.get_pos()
				self.title_screen.click((mx,my))
	def info_menu(self):
		#There is basically the same behaviour for every menu in the game
		# Wait for click, on click, run click function in object.
		# Everything related to state switching is inside those objects

		# only need to blit this once
		if self.info_screen.current_state == False:
			self.info_screen.current_state = True
			self.screen.blit(self.info_screen.image,self.info_screen.rect)
		
		for event in pygame.event.get():	
			if event.type == QUIT:
				sys.exit()
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.info_screen.click((mx,my))

	def win_menu(self):
	
		if self.win_screen.current_state == False:
			self.screen.fill((0,0,0))
			self.win_screen.current_state = True
			self.screen.blit(self.win_screen.image, self.win_screen.rect)
			# Display one of two win messages
			if self.state == PLAYER_1_DEAD:
				self.screen.blit(self.p2_win_text, (20,37))
			else:
				self.screen.blit(self.p1_win_text, (20,37))
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.win_screen.click((mx,my))


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
		
<<<<<<< HEAD
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
=======
			if event.type == KEYDOWN:
				binding = self.lookupBinding(event.key)
				if binding != "not found":
					self.inputState[binding] = True
			# If any key is released, and it is mapped, make its pressed status false		
			if event.type == KEYUP:
				binding = self.lookupBinding(event.key)
				if binding != "not found":
					self.inputState[binding] = False
			# idf mouse is pressed		
			if event.type == MOUSEBUTTONDOWN:
				#set click status to True
				self.inputState["click"] = True
>>>>>>> 349a47346bfc4b9b596bbcb107ab09738ef09d75

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
			obstacle = Obstacle((rand_x,rand_y),rand_type)
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
		self.player2 = Tank(self.turret2, "PLAYER_2", (400,500),self)
		#self.gameObjects.append(self.walls)
		self.players.append(self.player1)
		self.players.append(self.player2)
		self.create_obstacles()

class WorkHomeReceiver(LineReceiver):
	def __init__(self,addr):
		"""Constructor 
	for Server running, servicing work connections on home machine"""

	
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
	lc.start(1/5)

	#reactor.listenTCP(COMMAND_PORT, WorkHomeFactory())
	reactor.run()
	#reactor.run()
	lc.stop()
