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

PORT = 1025

class GroupProtocol(LineReceiver):

    def __init__(self, factory):

        self.factory = factory

    def connectionMade(self):

        print(self.factory.playerCount)
        if self.factory.playerCount == 4:
            self.sendLine("d".encode("ascii"))
            #self.loseConnection()
        else:
            for c in range(1,5):
                if self.factory.clients[c] == None:
                    self.factory.clients[c] = self
                    self.factory.clients[c].sendLine("c{}".format(str(c)).encode("ascii"))
                    self.factory.playerCount += 1
                    print("Adding player #{}".format(str(c)))
                    break

    def connectionLost(self, reason):

        for c in range(1,5):
            if self.factory.clients[c] == self:
                self.factory.clients[c] = None
                self.factory.playerCount -= 1
                print("Removing player #{}".format(str(c)))
                break

    def lineReceived(self, line):

        for c in range(1,5):
            if self.factory.clients[c] != None:
                source = u"<{}> ".format(self.transport.getPeer()).encode("ascii")
                self.factory.clients[c].sendLine(source + line)

class GroupFactory(Factory):
    def __init__(self):

        self.clients = {1: None,
                        2: None,
                        3: None,
                        4: None}
        self.playerCount = 0

    def buildProtocol(self, addr):
        return GroupProtocol(self)

factory = GroupFactory()
endpoint = TCP4ServerEndpoint(reactor, PORT)
endpoint.listen(factory)
reactor.run()
