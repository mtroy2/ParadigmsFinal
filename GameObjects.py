
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

class Walls(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		ss = spritesheet.spritesheet(os.getcwd() + "/tiles/walls.png")
		pygame.sprite.Sprite.__init__(self)
		self.image = ss.image_at((0,0,455,500))
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image) # pixel mask for collision detection


class Player1(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		ss = spritesheet.spritesheet(os.getcwd() + "/sprites/sprites.png")
		pygame.sprite.Sprite.__init__(self)
		self.image = ss.image_at((6,0,21,28))
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
