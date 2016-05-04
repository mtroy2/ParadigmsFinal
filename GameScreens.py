
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
	def __init__(self,player=None):
		# load pre-made image
		self.image = pygame.image.load(os.getcwd() + "/screens/Title_screen.png")
		self.rect = self.image.get_rect()
		# two rects - two buttons
		self.play_button = pygame.Rect(165,123,176,62)
		self.info_button = pygame.Rect(167,206,176,62)
		self.exit_button = pygame.Rect(370,0,130,46)
		self.player = player
		self.player.screen.blit(self.image, self.rect)
		self.current_state = True
		
	#sets next game state on click
	def click(self, click_point):
		# click was in play button
		if self.play_button.collidepoint(click_point):
			if self.player.state == TITLE_SCREEN:
				self.player.connect_to_server()
		elif self.exit_button.collidepoint(click_point):
			self.player.state = EXIT_GAME	
		# Paralyze all buttons after play button is pressed	

		elif self.info_button.collidepoint(click_point):
			if self.player.state != WAITING_1:
				self.player.state = INFO_SCREEN
				self.current_state = False

class Info_screen(pygame.sprite.Sprite):
	def __init__(self, player = None):
		self.image = pygame.image.load(os.getcwd()+ "/screens/Info_screen.png")	
		self.rect = self.image.get_rect()
		self.return_button = pygame.Rect(322,0,178,35)
		self.player = player
		self.current_state = False
	def click(self,click_point):
		if self.return_button.collidepoint(click_point):
			print "Button clicked, returning to title"
			self.player.state = TITLE_SCREEN	
			
			self.current_state = False	
class Win_screen(pygame.sprite.Sprite):
	def __init__(self,player = None):
		self.player = player
		self.image = pygame.image.load(os.getcwd()+"/screens/Win_screen.png")
		self.rect = self.image.get_rect()
		self.play_again_button = pygame.Rect(356,84,80,29)
		self.end_button = pygame.Rect(356,131,61,29)
		self.play_again_clicks = 0
		self.current_state = False		
	def click(self,click_point):
		if self.play_again_button.collidepoint(click_point):
			self.play_again_clicks +=1
			if self.play_again_clicks == 2:
				self.player.gs.reset()
				self.play_again_clicks = 0
				self.player.state = PLAYING
				self.current_state = False
		if self.end_button.collidepoint(click_point):
			self.player.gs.reset()
			self.player.state = TITLE_SCREEN
			self.current_state = False

		return self.player.state
	
