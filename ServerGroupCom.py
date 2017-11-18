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
        if self.factory.playerCount == 4 or self.factory.gameStarted:
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
                print("Removing player #" + str(c))
                break

    def dataReceived(self, line):

        move = line.decode()
        self.factory.movesList[int(move[1])-1] = move[0]
        self.factory.movesMade += 1

        if self.factory.movesMade == self.factory.playerCount:
            if self.factory.playerCount < 4:
                for c in range(1,5):
                    if self.factory.clients[c] == None:
                        #self.factory.movesList[c-1] = "u"
                        self.factory.movesList[c-1] = random.choice(["u", "d", "l", "r"])                             

            moves = ''.join(self.factory.movesList).encode()
            for c in range(1,5):
                if self.factory.clients[c] != None:
                    self.factory.clients[c].sendLine(moves)
            
            # Reset move variables
            self.factory.movesMade = 0
            self.factory.movesList = [0, 0, 0, 0]

    def scheduleStart(self):
        print("Game is starting...")
        self.factory.gameStarted = True
        for c in range(1,5):
            if self.factory.clients[c] != None:
                self.factory.clients[c].sendLine("s".encode())

class GroupFactory(Factory):
    def __init__(self):

        self.clients = {1: None,
                        2: None,
                        3: None,
                        4: None}
        self.playerCount = 0
        self.startScheduled = False
        self.gameStarted = False
        self.movesList = [0, 0, 0, 0]
        self.movesMade = 0

    def buildProtocol(self, addr):
        return GroupProtocol(self)

factory = GroupFactory()
endpoint = TCP4ServerEndpoint(reactor, PORT)
endpoint.listen(factory)
reactor.run()
