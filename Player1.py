# Client.py
# Test class to test Server.py

from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from GameSpace import GameSpace
from GameObjects import *
from GameScreens import *
from GameConstants import *
import cPickle as pickle


class ClientConn(LineReceiver):
	def __init__(self, player):
		self.player = player
		self.name = "PLAYER_1"
		self.state = WAITING_2
		self.player.add_connection(self)
	def connectionMade(self):
		self.sendLine(self.name)

	def lineReceived(self,line):
		line = pickle.loads(line)
		if self.state != PLAYING:
			if line["type"] == "GOTO_WAITING":
				self.player.state = WAITING_1
				self.state = WAITING_1

			elif line["type"] == "GOTO_PLAYING": 
				i = 0
				for obstacle in self.player.gs.game_obstacles:
					obstacle.rect.center = line["obstacles"][i]
					i += 1
				self.player.state = PLAYING
				self.state = PLAYING
		else:
			if line["type"] == "GOTO_MENU":
				self.player.state = TITLE_SCREEN
				self.state = TITLE_SCREEN
				self.transport.loseConnection()
			elif line["type"] == "UPDATE":
				p1dict = line["player1"]
				p2dict = line["player2"]
				self.player.gs.players[0].rect.center = p1dict["rect_center"]
				self.player.gs.players[0].angle = p1dict["angle"]
				self.player.gs.players[0].health = p1dict["health"]
				self.player.gs.players[0].ammo = p1dict["ammo"]
				self.player.gs.players[0].turret.rect.center = p1dict["turret_center"]
				self.player.gs.players[0].turret.angle = p1dict["turret_angle"]
				self.player.gs.players[0].transform_img()
				self.player.gs.players[0].turret.transform_img(self.player.gs.players[0].rect.center)
				self.player.gs.players[1].rect.center = p2dict["rect_center"]
				self.player.gs.players[1].angle = p2dict["angle"]
				self.player.gs.players[1].health = p2dict["health"]
				self.player.gs.players[1].ammo = p2dict["ammo"]
				self.player.gs.players[1].turret.rect.center = p2dict["turret_center"]
				self.player.gs.players[1].turret.angle = p2dict["turret_angle"]
				self.player.gs.players[1].transform_img()
				self.player.gs.players[1].turret.transform_img(self.player.gs.players[1].rect.center)
				bullet_dict = line["bullets"]
				if line["make_bullet"] == True:
					self.player.gs.create_bullet( bullet_dict[-1]["center"], bullet_dict[-1]["angle"] )

				if self.player.gs.players[0].health <= 0:
					self.player.state = PLAYER_1_DEAD
				elif self.player.gs.players[1].health <= 0:
					self.player.state = PLAYER_2_DEAD

	def connectionLost(self, reason):
		print 'lost connection to', SERVER_HOST, 'port', SERVER_PORT
		#reactor.stop()

class ClientConnFactory(ClientFactory):
	def __init__(self, player):
		self.player = player

	def buildProtocol(self, addr):
		return ClientConn(self.player)

class Player:
	def __init__(self,gs=None,player=None):
		self.gs = gs
		self.name = player
		self.state = TITLE_SCREEN
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
		self.gs.connect_player(self)
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
				reactor.stop()
				sys.exit()
			if event.type == MOUSEBUTTONUP:
				mx,my = pygame.mouse.get_pos()
				self.win_screen.click((mx,my))

	def active_game(self):
		# Send data to server
		data = {}
		data["player"] = 0
		self.inputState["click"] = False
		for event in pygame.event.get():
			if event.type == QUIT:
				self.connection.transport.loseConnection()
				reactor.stop()
				sys.exit()
			elif event.type == KEYDOWN:
				binding = self.lookupBinding(event.key)
				if binding != "not found":
					self.inputState[binding] = True
			elif event.type == KEYUP:
				binding = self.lookupBinding(event.key)
				if binding != "not found":
					self.inputState[binding] = False
			elif event.type == MOUSEBUTTONDOWN:
				self.inputState["click"] = False
			elif event.type == MOUSEBUTTONUP:
				self.inputState["click"] = True

		data["mouse"] = pygame.mouse.get_pos()
		data["inputState"] = self.inputState
		data = pickle.dumps(data)
		self.connection.sendLine(data)

		# Redraw all objects on screen
		self.screen.fill((0,0,0))
		# redraw map
		self.screen.blit(self.map.image, self.map.rect)
		#redraw bushes
		for bush in self.gs.game_obstacles:
			self.screen.blit(bush.image, bush.rect)

		# Redraw player
		for player in self.gs.players:
			self.screen.blit(player.image, player.rect)
			self.screen.blit(player.turret.image, player.turret.rect)

		# Redraw bullets
		for bullet in self.gs.bullets:
			bullet.tick()
			self.screen.blit(bullet.image,bullet.rect)
		# Draw ammo and health
		self.draw_health_bars()	
		self.show_ammo()

		pygame.display.flip()


	def draw_health_bars(self):
		pygame.draw.rect(self.screen, (255,0,0), (103,36, self.gs.player1.health, 15))
		pygame.draw.rect(self.screen, (255,0,0), (346,36, self.gs.player2.health, 15))
		
	def show_ammo(self):
		p1_ammo_line = str(self.gs.player1.ammo)
		p2_ammo_line = str(self.gs.player2.ammo)
		p1_ammo_text = self.font.render(p1_ammo_line,1,(255,255,255))
		p2_ammo_text = self.font.render(p2_ammo_line,1,(255,255,255))
		self.screen.blit(p1_ammo_text, (85,64))
		self.screen.blit(p2_ammo_text, (330,64))
	def connect_to_server(self):
		reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory(self))
	def add_connection(self,connection):
		self.connection = connection
		print 'player connected'
	
if __name__ == '__main__':

	gs = GameSpace()
	Player = Player(gs,	"PLAYER_1")
	lc = LoopingCall(Player.main)
	lc.start(1/10)

	reactor.run()
