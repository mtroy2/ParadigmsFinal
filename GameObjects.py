
import sys
import os
import pygame
from pygame.locals import *


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
TITLE_SCREEN = 0
WAITING_2 = 1
WAITING_1 = 2
INFO_SCREEN = 3
WAITING_FOR_PLAYER = 4
PLAYING = 5
PLAYER_1_DEAD = 6
PLAYER_2_DEAD = 7


class Walls(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		self.NAME = "WALLS"
		self.walls = pygame.sprite.Group()
		ss = spritesheet.spritesheet(os.getcwd() + "/tiles/walls.png")
		pygame.sprite.Sprite.__init__(self)
		#self.image = ss.image_at((0,0,455,500))
		self.wall1 = ss.image_at((0,0,455,14))
		self.image = ss.image_at((117,35,73,40))
		self.image.set_colorkey((0,0,0))
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image) # pixel mask for collision detection
	def tick(self):
		pass

class Turret(pygame.sprite.Sprite):
	def __init__(self,owner,gs=None):
		self.gs = gs
		self.NAME = "TURRET"
		if owner == "PLAYER_1":
			self.image = pygame.image.load(os.getcwd()+ "/sprites/P1_turret.png").convert_alpha()
		else:
			self.image = pygame.image.load(os.getcwd()+"/sprites/P2_turret.png").convert_alpha()
		pygame.sprite.Sprite.__init__(self)
		self.orig_image = self.image
		self.rect = self.image.get_rect()
		self.length =26 #px
		self.angle = math.radians(270)
	def assign_center(self,center):
		self.rect.center = center
	#rotate to face mouse location
	def tick(self,tank_center):

		#get mouse x and y
		mx,my = pygame.mouse.get_pos()
		# get coordinates btwn mouse and center of player
		dx = mx - self.rect.centerx
		dy = self.rect.centery - my
		oldCenter = self.rect.center
		if dx != 0:
		# set angle - initial offset of mouth
			self.angle = math.atan2(dy,dx) 
			if self.angle < 0:
				# make angle always in positive radians
				self.angle += (math.pi * 2)
			self.image = pygame.transform.rotate(self.orig_image,math.degrees(self.angle ) + 90)
			rotRectangle = self.image.get_rect()
			rotRectangle.center = tank_center
			self.rect = rotRectangle



	def rot_point(self,point,axis,ang):
		x,y = point[0] - axis[0], point[1] - axis[1]
		radius = math.sqrt(x*x + y*y)
		h = axis[0]+ (radius * math.cos(ang))
		v = axis[1] + (radius * math.sin(ang))
		return h,v			
class Tank(pygame.sprite.Sprite):
	def __init__(self,turret,player,center,gs=None):
		self.gs = gs
		self.NAME = "TANK"
		self.PLAYER = player
		pygame.sprite.Sprite.__init__(self)
		if player == "PLAYER_1":
			self.image = pygame.image.load(os.getcwd()+ "/sprites/P1_tank.png").convert_alpha()
		else:
			self.image = pygame.image.load(os.getcwd()+"/sprites/P2_tank.png").convert_alpha()
		self.orig_image = self.image
		self.rect = self.image.get_rect()
		self.rect.center = center  # correct point is 227,378
		self.turret = turret
		self.turret.assign_center((center[0],center[1]+10))
		self.mask = pygame.mask.from_surface(self.image)
		self.angle = math.radians(270)
		self.speed = .5
		self.dy =  math.sin(self.angle) * self.speed
		self.dx = math.cos(self.angle) * self.speed
		self.currentx = float(self.rect.centerx)
		self.currenty = float(self.rect.centery)
		self.health = 100
	def tick(self):
		self.turret.tick(self.rect.center)
	def do_damage(self,damage):
		self.health -= damage
		if self.health <= 0:
			if self.PLAYER == "PLAYER_1":
				self.gs.state = PLAYER_1_DEAD
			else:
				self.gs.state = PLAYER_2_DEAD 
	def click(self):
		self.gs.create_bullet(self.rect.center,self.turret.angle)
	def move(self, direction):
		collision_detected = 0

		if direction == "up":
			mask_point = None
			for bush in self.gs.game_obstacles:
				# if rectangles overlap
				if self.rect.colliderect(bush.rect):
					mask_point = pygame.sprite.collide_mask(self,bush)
					if mask_point != None:
						print "Mask overlap"
						collision_detected = 1
						mask_y = mask_point[1]
			# no collision with bushes
			if not mask_point:
				if (self.currentx + self.dx > 500) or (self.currentx + self.dx <= 0) or (self.currenty -self.dy <=100) or (self.currenty -self.dy >= 600):
					self.currentx -= self.dx
					self.currenty += self.dy
					# set rect center to x,y 
					self.rect.centerx = self.currentx
					self.rect.centery = self.currenty

					self.turret.rect.centerx = self.currentx
					self.turret.rect.centery = self.currenty
				else:
					self.currentx += self.dx
					self.currenty -= self.dy
					# set rect center to x,y 
					self.rect.centerx = self.currentx
					self.rect.centery = self.currenty
					self.turret.rect.centerx = self.currentx
					self.turret.rect.centery = self.currenty
			else:
				# collision on the back of the tank while going forward (OK)
				if mask_y < 25:
					self.currentx += self.dx
					self.currenty -= self.dy
					# set rect center to x,y 
					self.rect.centerx = self.currentx
					self.rect.centery = self.currenty

					self.turret.rect.centerx = self.currentx
					self.turret.rect.centery = self.currenty
				else:
					self.currentx -= self.dx
					self.currenty += self.dy
					# set rect center to x,y 
					self.rect.centerx = self.currentx
					self.rect.centery = self.currenty

					self.turret.rect.centerx = self.currentx
					self.turret.rect.centery = self.currenty
		if direction == "down":
			mask_point = None
			for bush in self.gs.game_obstacles:
				# if rectangles overlap
				if self.rect.colliderect(bush.rect):
					mask_point = pygame.sprite.collide_mask(self,bush)
					if mask_point != None:
						collision_detected = 1
						mask_y = mask_point[1]
			if not mask_point:
				self.currentx -= self.dx
				self.currenty += self.dy
				# set rect center to x,y 
				self.rect.centerx = self.currentx
				self.rect.centery = self.currenty

				self.turret.rect.centerx = self.currentx
				self.turret.rect.centery = self.currenty
			# found collision
			else:
				# collision on front of tank, we are going reverse, so keep going
		
				if mask_point[1] > 25:
					self.currentx -= self.dx
					self.currenty += self.dy
					# set rect center to x,y 
					self.rect.centerx = self.currentx
					self.rect.centery = self.currenty

					self.turret.rect.centerx = self.currentx
					self.turret.rect.centery = self.currenty

				else:
					self.currentx += self.dx
					self.currenty -= self.dy
					# set rect center to x,y 
					self.rect.centerx = self.currentx
					self.rect.centery = self.currenty

				self.turret.rect.centerx = self.currentx
				self.turret.rect.centery = self.currenty
	def rotate(self,direction):
		if direction == "left":
			oldCenter = self.rect.center		# if rectangles overlap

			self.angle = self.angle +math.radians(1)
			if self.angle > 2*math.pi:
				self.angle = self.angle - 2*math.pi

			elif self.angle < -2*math.pi:
				self.angle = self.angle + 2*math.pi
			self.image = pygame.transform.rotate(self.orig_image,math.degrees(self.angle)-270)
			rotRectangle = self.image.get_rect()
			rotRectangle.center = oldCenter
			self.rect = rotRectangle
			
		else:
			oldCenter = self.rect.center
			self.angle = self.angle -math.radians(1)

			if self.angle > 2*math.pi:
				self.angle = self.angle - 2*math.pi
			elif self.angle < -2*math.pi:
				self.angle = self.angle + 2*math.pi
			self.image = pygame.transform.rotate(self.orig_image,math.degrees(self.angle)-270)
			rotRectangle = self.image.get_rect()
			rotRectangle.center = oldCenter
			self.rect = rotRectangle
		self.dy =  math.sin(self.angle ) * self.speed
		self.dx = math.cos(self.angle) * self.speed


class Map(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		self.gs = gs
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(os.getcwd() + "/tiles/battleground.png")
		self.rect = self.image.get_rect()

class Obstacle(pygame.sprite.Sprite):
	def __init__(self,center,code,gs=None):
		self.gs = gs
		self.NAME = "OBSTACLE"
		pygame.sprite.Sprite.__init__(self)
		if code == 1: # big bush
			self.image =  pygame.image.load(os.getcwd() + "/sprites/Big_bush.png").convert_alpha()
		elif code == 2:
			self.image = pygame.image.load(os.getcwd()+ "/sprites/Small_bush.png").convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.mask = pygame.mask.from_surface(self.image)
	def tick(self):
		pass

class Bullet(pygame.sprite.Sprite):
	def __init__(self, center=(0.0,0.0), angle=0.0, ID=-1,gs=None,):
		self.center = center
		self.angle = angle
		self.total_distance = 0.0
		self.damage = 20
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.NAME = "BULLET"
		self.ID = ID
		self.image= pygame.image.load(os.getcwd()+ "/sprites/Bullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.angle = angle
		self.velocity = 1
		self.dy =  math.sin(self.angle) * self.velocity
		self.dx = math.cos(self.angle) * self.velocity
		self.dist_per_tick = math.sqrt( math.fabs(self.dx)*math.fabs(self.dx) + math.fabs(self.dy)*math.fabs(self.dy))
        # these two handle the fact that you can't update an image by less than 1 pixel
        # they keep track of the running total of movement, as floats
		self.currentx = float(self.rect.centerx)
		self.currenty = float(self.rect.centery)
		self.mask = pygame.mask.from_surface(self.image)
	def tick(self):
		# update x,y
		self.total_distance = self.total_distance + self.dist_per_tick
		if (self.total_distance > 300):
			self.gs.delete_bullet(self.ID)
 		hit_bush = 0
		hit_player = 0
		for bush in self.gs.game_obstacles :
			# if rectangles overlap
			if self.rect.colliderect(bush.rect):
				if pygame.sprite.collide_mask(self, bush) != None:
					hit_bush = 1
		if self.total_distance > 15:
			for player in self.gs.players:
				if self.rect.colliderect(player.rect):
					if pygame.sprite.collide_mask(self,player) != None:
						player.do_damage(self.damage)
						hit_player = 1
		if hit_bush == 1 or hit_player == 1:
			self.gs.delete_bullet(self.ID)

	
		else:
			self.currentx += self.dx
			self.currenty -= self.dy
			# set rect center to x,y 
			self.rect.centerx = self.currentx
			self.rect.centery = self.currenty
        	# hit left side of screen
			if  (self.rect.centerx >= self.gs.width) or (self.rect.centerx <= 0) :
				self.dx = self.dx * -1
		 	elif (self.rect.centery >= 600) or  (self.rect.centery <= 100):
				self.dy = self.dy * -1
		
