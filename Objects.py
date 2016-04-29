
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
		ss = spritesheet.spritesheet(os.getcwd() + "/tiles/map.png")
		pygame.sprite.Sprite.__init__(self)
		self.image = ss.image_at((0,0,455,500))
		self.mask = pygame.mask_from_surface(self.image) # pixel mask for collision detection
