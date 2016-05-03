
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
from GameConstants import *

class Title_screen(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		# load pre-made image
		self.image = pygame.image.load(os.getcwd() + "/screens/Title_screen.png")
		self.rect = self.image.get_rect()
		# two rects - two buttons
		self.play_button = pygame.Rect(165,123,176,62)
		self.info_button = pygame.Rect(167,206,176,62)
		self.exit_button = pygame.Rect(370,0,130,46)
		self.gs = gs
		self.gs.screen.blit(self.image, self.rect)
		self.current_state = True
		
	#sets next game state on click
	def click(self, click_point):
		# click was in play button
		if self.play_button.collidepoint(click_point):
			if self.gs.state == WAITING_2:
				self.gs.connect_to_server()
				self.gs.state = WAITING_1
			elif self.gs.state == WAITING_1:
				self.gs.show_ammo()
				self.gs.state = PLAYING
				self.current_state = False
			self.gs.screen.fill ((0,0,0))
			

		elif self.info_button.collidepoint(click_point):
			
			self.gs.state = INFO_SCREEN
			self.current_state = False
		elif self.exit_button.collidepoint(click_point):
			self.gs.state = EXIT_GAME
class Info_screen(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.image = pygame.image.load(os.getcwd()+ "/screens/Info_screen.png")	
		self.rect = self.image.get_rect()
		self.return_button = pygame.Rect(322,0,178,35)
		self.gs = gs
		self.current_state = False
	def click(self,click_point):
		if self.return_button.collidepoint(click_point):
			print "Button clicked, returning to title"
			self.gs.state = WAITING_2	
			
			self.current_state = False	
class Win_screen(pygame.sprite.Sprite):
	def __init__(self,gs = None):
		self.gs = gs
		self.image = pygame.image.load(os.getcwd()+"/screens/Win_screen.png")
		self.rect = self.image.get_rect()
		self.play_again_button = pygame.Rect(356,84,80,29)
		self.end_button = pygame.Rect(356,131,61,29)
		self.play_again_clicks = 0
		self.current_state = False		
	def click(self,click_point):
		self.gs.reset()
		if self.play_again_button.collidepoint(click_point):
			self.play_again_clicks +=1
			if self.play_again_clicks == 2:
				self.play_again_clicks = 0
				self.gs.state = PLAYING
				self.current_state = False
		if self.end_button.collidepoint(click_point):
			self.gs.state = WAITING_2
			self.current_state = False
	
