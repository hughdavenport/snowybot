#!/usr/bin/env python

"""A really simple IRC bot."""

import sys
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc

joined = []

class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)


    def signedOn(self):
        """ Join ALL THE CHANNELS """
        print "Signed on"
        self.sendLine("/list")
        self.join("#snowy")
        print self.whois(self.factory.follownick)

    def joined(self, channel):
        print "Joined channel %s" % channel
        global joined
        joined.append(channel)

    def left(self, channel):
        print "Left channel %s" % channel
        global joined
        print joined
        joined.remove(channel)

    def userJoined(self, user, channel):
        print "User %s joined %s" % (user, channel)

    def userLeft(self, user, channel):
        print "User %s parted %s" % (user, channel)
        self.msg(channel, "WOOF WOOF")
        if user == self.factory.follownick:
            self.leave(channel)

    def userQuit(self, user, channel):
        print "User %s quit %s" % (user, channel)
        if user == self.factory.follownick:
            self.leave(channel)

    def userKicked(self, user, channel, kicker):
        print "User %s kicked from %s by %s" % (user, channel, kicker)
        if user == self.factory.follownick:
            self.leave(channel)

    def userRenamed(self, olduser, newuser):
        print "User %s renamed to %s" % (olduser, newuser)
        if olduser == self.factory.follownick:
            self.factory.follownick = newuser

    def irc_RPL_WHOISCHANNELS(self, prefix, params):
        global joined
        channels = params[2].strip().split(' ')
        for channel in channels:
            channel = channel.lstrip('@')
            try:
                joined.index(channel)
            except Error:
                self.join(channel)

    def lineReceived(self, line):
        print "Got line %s" % line
        irc.IRCClient.lineReceived(self, line)


class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, nickname='snowy', follownick='hugh'):
        self.nickname = nickname
        self.follownick = follownick

    def clientConnectionLost(self, connector, reason):
        print "Connection lost. Reason: %s" % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed. Reason: %s" % reason

if __name__ == "__main__":
    reactor.connectTCP('irc', 6667, BotFactory())
    reactor.run()
