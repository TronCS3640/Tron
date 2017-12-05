#!/usr/bin/env python3

# Server Commands
# c#: connect new player and send them they're player#
# d#: disconnect player
#
# Player Commands
# {u|d|l|r}# send to all players (this is the movement command)
# k# send to all players (removes player # from play)

# if player doesn't respond, drop player

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from sys import stdout, argv
import threading
import random

PORT = 1025

class GroupProtocol(LineReceiver):

    def __init__(self, factory):

        self.factory = factory

    def connectionMade(self):

        # Reject connections if enough players or game is running
        if self.factory.playerCount == 4 or self.factory.gameStarted:
            self.transport.abortConnection()
        # Add client to dictionary
        else:
            for c in range(1,5):
                if self.factory.clients[c] == None:
                    print("Adding player #" + str(c))
                    self.factory.clients[c] = self
                    line = "c" + str(c)
                    self.factory.clients[c].sendLine(line.encode())
                    self.factory.playerCount += 1
                    break

            # Begin countdown to game start
            if not self.factory.startScheduled:
                if self.factory.playerCount == 1:
                    self.factory.startScheduled = True
                    print("Game will start in {} seconds...".format(str(self.factory.countdown)))
                    reactor.callLater(self.factory.countdown, self.scheduleStart)
                    #print("Game will start in 10 seconds...")
                    #reactor.callLater(10, self.scheduleStart)

    def connectionLost(self, reason):

        # Remove player and pass player control to server
        for c in range(1,5):
            if self.factory.clients[c] == self:
                print("Removing player #" + str(c))
                self.factory.clients[c] = None
                self.factory.playerCount -= 1
                self.factory.cpuPlayers.add(c)
                self.processMove("u", c)
                break

    def dataReceived(self, line):

        # Schedule timer to force moves if response take too long
        if not self.factory.collectionStarted:
            self.factory.collectionStarted = True
            threading.Timer(.2, self.forceMoves).start()

        # Process moves if there is not already a winner
        if not self.factory.isWinner:
            move = line.decode()
            self.processMove(move[0], int(move[1]))

    def processMove(self, move, pnum):

        # If player dies, server sends "k" to other players from then on
        if move == "k" and pnum not in self.factory.deadPlayers:
            self.factory.deadPlayers.add(pnum)
            if pnum not in self.factory.cpuPlayers:
                self.factory.cpuPlayers.add(pnum)
                self.factory.playerCount -= 1
        # If player wins notify others with "w" and schedule game reset
        elif move == "w":
            print("Player has won")
            self.factory.movesList = ["k", "k", "k", "k"]
            self.factory.movesList[pnum-1] = "w"
            self.factory.cpuPlayers.add(pnum)
            self.factory.playerCount = 0
            self.factory.isWinner = True
            reactor.callLater(1, self.scheduleReset)
        # If no special cases just store the move normally
        else:
            self.factory.movesList[pnum-1] = move
            self.factory.movesMade += 1

        # Server sends formatted move list to clients 
        if self.factory.movesMade >= self.factory.playerCount:
            if self.factory.playerCount > 0 and self.factory.playerCount < 4:
                # Server makes moves for dead and cpu players
                for c in self.factory.cpuPlayers:
                    if c in self.factory.deadPlayers:
                        self.factory.movesList[c-1] = "k"
                    else:
                        self.factory.movesList[c-1] = random.choice(["u", "d", "l", "r"])

            moves = ''.join(self.factory.movesList).encode()
            #print("sending:\t" + moves.decode())
            for c in range(1,5):
                if self.factory.clients[c] != None:
                    self.factory.clients[c].sendLine(moves)

            # Reset move variables
            self.factory.movesMade = 0
            self.factory.movesList = [0, 0, 0, 0]
            self.factory.collectionStarted = False

    def forceMoves(self):
        # Server makes move for players that are taking too long to respond
        if self.factory.collectionStarted:
            for p in range(0,4):
                if self.factory.movesList[p] == 0:
                    self.factory.mutex.acquire()
                    self.processMove("u", p-1)
                    self.factory.mutex.release()
            self.factory.collectionStarted = False

    def scheduleStart(self):
        # Set up game and send "s" to let players know to start
        print("Game is starting...")
        self.factory.gameStarted = True
        self.factory.deadPlayers = set()
        self.factory.cpuPlayers = set()
        for c in range(1,5):
            if self.factory.clients[c] == None:
                self.factory.cpuPlayers.add(c)
        #print(self.factory.cpuPlayers)
        for c in range(1,5):
            if c not in self.factory.cpuPlayers:
                self.factory.clients[c].sendLine("s".encode())
        # Remove when done testing
        self.factory.startScheduled = False

    def scheduleReset(self):
        # Reset game after round has completed
        print("Game is reseting...")
	    # Reset game variables
        self.factory.gameStarted = False
        self.factory.isWinner = False
        self.factory.deadPlayers = set()
        self.factory.cpuPlayers = set()
        # Disconnect current connections so new players can play
        for c in range(1,5):
            if self.factory.clients[c] != None:
                self.factory.clients[c].transport.abortConnection()
                self.factory.clients[c] = None

class GroupFactory(Factory):

    def __init__(self):

        print("Server Port: " + str(PORT))
        self.clients = {1: None,
                        2: None,
                        3: None,
                        4: None}
        self.cpuPlayers = set()
        self.deadPlayers = set()
        self.playerCount = 0
        self.startScheduled = False
        self.collectionStarted = False
        self.gameStarted = False
        self.isWinner = False
        self.mutex = threading.Lock()
        self.movesList = [0, 0, 0, 0]
        self.movesMade = 0

        try:
                self.countdown = int(argv[1])
        except:
                self.countdown = 10

    def buildProtocol(self, addr):
        return GroupProtocol(self)

# Set up server
factory = GroupFactory()
endpoint = TCP4ServerEndpoint(reactor, PORT)
endpoint.listen(factory)
reactor.run()
