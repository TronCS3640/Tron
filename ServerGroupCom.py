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
from sys import stdout
import random

PORT = 1025

class GroupProtocol(LineReceiver):

    def __init__(self, factory):

        self.factory = factory

    def connectionMade(self):

        # Reject connections if enough players or game is running
        if self.factory.playerCount == 4:
        #if self.factory.playerCount == 4 or self.factory.gameStarted:
            self.transport.abortConnection()

        else:
            for c in range(1,5):
                if self.factory.clients[c] == None:
                    self.factory.clients[c] = self
                    line = "c" + str(c)
                    self.factory.clients[c].sendLine(line.encode())
                    self.factory.playerCount += 1
                    print("Adding player #" + str(c))
                    break

            # Begin countdown to game start
            if not self.factory.startScheduled:
                #if self.factory.playerCount == 2:
                if self.factory.playerCount == 1:
                    self.factory.startScheduled = True
                    print("Game will start in 10 seconds...")
                    reactor.callLater(3, self.scheduleStart)
                    #reactor.callLater(10, self.scheduleStart)

    def connectionLost(self, reason):

        for c in range(1,5):
            if self.factory.clients[c] == self:
                self.factory.clients[c] = None
                self.factory.playerCount -= 1
                self.factory.cpuPlayers.add(c)
                self.processMove("u", c)
                print("Removing player #" + str(c))
                break

    def dataReceived(self, line):

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
        elif move == "w":
            print("Player has won")
            self.factory.movesList = ["k", "k", "k", "k"]
            self.factory.movesList[pnum-1] = "w"
            self.factory.cpuPlayers.add(pnum)
            self.factory.playerCount = 0
            self.factory.isWinner = True
            reactor.callLater(3, self.scheduleReset)
        else:
            self.factory.movesList[pnum-1] = move
            self.factory.movesMade += 1

        # Server makes moves for dead and cpu players
        if self.factory.movesMade >= self.factory.playerCount:
            if self.factory.playerCount > 0 and self.factory.playerCount < 4:
                for c in self.factory.cpuPlayers:
                    if c in self.factory.deadPlayers:
                        self.factory.movesList[c-1] = "k"
                    else:
                        self.factory.movesList[c-1] = random.choice(["u", "d", "l", "r"])

            print(self.factory.movesList)
            moves = ''.join(self.factory.movesList).encode()
            #print("sending:\t" + moves.decode())
            for c in range(1,5):
                if self.factory.clients[c] != None:
                    self.factory.clients[c].sendLine(moves)

            # Reset move variables
            self.factory.movesMade = 0
            self.factory.movesList = [0, 0, 0, 0]

    def scheduleStart(self):
        print("Game is starting...")
        self.factory.gameStarted = True
        self.factory.deadPlayers = set()
        self.factory.cpuPlayers = set()
        for c in range(1,5):
            if self.factory.clients[c] == None:
                self.factory.cpuPlayers.add(c)
        print(self.factory.cpuPlayers)
        for c in range(1,5):
            if c not in self.factory.cpuPlayers:
                self.factory.clients[c].sendLine("s".encode())
        # Remove when done testing
        self.factory.startScheduled = False

    def scheduleReset(self):
        print("Game is reseting...")
        # Disconnect current connections so new players can play
        self.factory.gameStarted = False
        self.factory.isWinner = False
        self.factory.deadPlayers = set()
        self.factory.cpuPlayers = set()
        for c in range(1,5):
            if self.factory.clients[c] != None:
                self.factory.clients[c].transport.abortConnection()
                self.factory.clients[c] = None

class GroupFactory(Factory):
    def __init__(self):

        self.clients = {1: None,
                        2: None,
                        3: None,
                        4: None}
        self.cpuPlayers = set()
        self.deadPlayers = set()
        self.playerCount = 0
        self.startScheduled = False
        self.gameStarted = False
        self.isWinner = False
        self.movesList = [0, 0, 0, 0]
        self.movesMade = 0

    def buildProtocol(self, addr):
        return GroupProtocol(self)

factory = GroupFactory()
endpoint = TCP4ServerEndpoint(reactor, PORT)
endpoint.listen(factory)
reactor.run()
