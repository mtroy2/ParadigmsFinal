# Client.py
# Test class to test Server.py

from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from PyGame import GameSpace
from GameObjects import *
from GameScreens import *
from GameConstants import *


class ClientConn(LineReceiver):
	def __init__(self, gamestate):

		self.gs = gamestate
		self.name = "PLAYER_2"

	def connectionMade(self):
		self.sendLine(self.name)

	def lineReceived(self,line):
		print line

	def connectionLost(self, reason):
		print 'lost connection to', SERVER_HOST, 'port', SERVER_PORT
		reactor.stop()

	def sendEvent(self, event):
		data = {}
		data["player"] = self.player
		data["event"] = cmd
		data = pickle.dumps(data)
		self.transport.write(data)

class ClientConnFactory(ClientFactory):
	def __init__(self, gamestate):
		self.gs = gamestate

	def buildProtocol(self, addr):
		return ClientConn(self.gs)

class Player:
	def __init__(self,gs=None,player=None):
		self.gs = gs
		self.name = player
		self.state = WAITING_2
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
		self.size = self.width,self.height = 500,700
		self.screen = pygame.display.set_mode(self.size)
		self.map = Map(self)
		# init screens
		self.info_screen = Info_screen(self)
		self.title_screen = Title_screen(self)
		self.win_screen = Win_screen(self)
		


		# font to be used for any text displayed on screen
		self.font = pygame.font.SysFont("monospace",15)
		# Text to be displayed on screen
		self.waiting_text_state = 1
		self.waiting_text_1 = self.font.render("Waiting for other player.",1,(255,255,255))
		self.waiting_text_2 = self.font.render("Waiting for other player..",1,(255,255,255))
		self.waiting_text_3 = self.font.render("Waiting for other player...",1,(255,255,255))
		self.p1_win_text = self.font.render("PLAYER 1 WINS!",1,(255,255,255))
		self.p2_win_text = self.font.render("PLAYER 2 WINS!",1,(255,255,255))
		
		# 	game counters 
		self.waiting_counter = 0.0
	
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
		# Main switches based on current state of game
		# only need to blit this once
	
		if not self.info_screen.current_state:
	
			self.info_screen.current_state = True
			self.screen.blit(self.info_screen.image,self.info_screen.rect)
		
		for event in pygame.event.get():	
			if event.type == QUIT:
				sys.exit()
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.info_screen.click((mx,my))
	# Main switches based on current state of game
	def win_menu(self):
	
		if self.win_screen.current_state == False:
			self.screen.fill((0,0,0))
			self.win_screen.current_state = True
			self.screen.blit(self.win_screen.image, self.win_screen)	# Main switches based on current state of game.rect
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

	def connect_to_server(self):
		reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory(self.gs))


	
if __name__ == '__main__':

	gs = GameSpace()
	Player = Player("PLAYER_2",gs)
	lc = LoopingCall(Player.main)
	lc.start(1/10)

	reactor.run()
