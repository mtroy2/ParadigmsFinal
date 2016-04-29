
import sys
import os
import pygame
from pygame.locals import *

from Player import Player
from Laser import Laser
from USC import USC
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

class Map(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		ss = spritesheet.spritesheet(os.getcwd() + "/tiles/map.png")
		pygame.sprite.Sprite.__init__(self)
		self.image = 

