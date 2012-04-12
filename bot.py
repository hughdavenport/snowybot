#!/usr/bin/env python

"""A really simple IRC bot."""

import sys
from twisted.internet import reactor, protocol
from twisted.internet.task import LoopingCall
from twisted.words.protocols import irc

joined = []

class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)


    def signedOn(self):
        """ Join ALL THE CHANNELS """
        print "Signed on"
        lc = LoopingCall(self.whois, self.factory.follownick)
        lc.start(10)

    def joined(self, channel):
        print "Joined channel %s" % channel
        global joined
        joined.append(channel)

    def left(self, channel):
        print "Left channel %s" % channel
        global joined
        joined.remove(channel)

    def kickedFrom(self, channel, kicker, message):
        print "Kicked from channel %s by %s (%s)" % (channel, kicker, message)
        global joined
        joined.remove(channel)
        self.join(channel)

    def userJoined(self, user, channel):
        print "User %s joined %s" % (user, channel)

    def userLeft(self, user, channel):
        print "User %s parted %s" % (user, channel)
        self.msg(channel, "WOOF WOOF")
        if user == self.factory.follownick:
            self.leave(channel)

    def userQuit(self, user, reason):
        print "User %s quit (%s)" % (user, reason)
        if user == self.factory.follownick:
            self.leave(channel)

    def userKicked(self, user, channel, kicker, message):
        print "User %s kicked from %s by %s (%s)" % (user, channel, kicker, message)
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
            if not channel in joined:
                self.join(channel)

    def privmsg(self, user, channel, message):
        print 'channel: `%s` user: `%s` msg: `%s`' % (user, channel, message)

    def lineReceived(self, line):
        #print "Got line %s" % line
        irc.IRCClient.lineReceived(self, line)


class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, nickname='snowy', follownick='tintin'):
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
