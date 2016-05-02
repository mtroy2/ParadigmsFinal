# Client.py
# Test class to test Server.py

from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.task import LoopingCall
from PyGame import GameSpace

SERVER_HOST = 'localhost'
SERVER_PORT = 9000

class ClientConn(Protocol):
	def __init__(self, gamestate, dummy1, dummy2, dummy3):
		gamestate.conn = self
		self.gs = gamestate
		self.gs

	def connectionMade(self):
		print 'successfully connected to', SERVER_HOST, 'port', SERVER_PORT

	def dataReceived(self, data):
		info = pickle.loads(data)
		#self.gs.players = info["players"]
		#self.gs.bullets = info["bullets"]
		print 'data received:', data

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
		return ClientConn(self.gs, "dummy", "dummy", "dummy")


if __name__ == '__main__':
	gs = GameSpace("client")
	lc = LoopingCall(gs.main)
	lc.start(1/60)
	reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory(gs))
	reactor.run()
