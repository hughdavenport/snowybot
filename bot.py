#!/usr/bin/env python

"""A really simple IRC bot."""

import time
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
        if user == self.factory.follownick:
            self.msg(channel, "WOOF WOOF")
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
#            if channel != '#lunch':
#                continue
            if not channel in joined:
                print "Trying to join %s" % channel
                self.join(channel)

    def privmsg(self, user, channel, msg):
	if '!' in user:
	    user = user[:user.index('!')]
        if channel == self.factory.nickname:
            print '*%s* %s' % (user, msg)
            sendto = user
        else:
            print '%s: <%s> %s' % (channel, user, msg)
            sendto = channel
#        if msg.startswith('!'):
#            self.act( user, sendto, msg[1:] )
        if msg.startswith(self.factory.nickname + ': '):
            self.act( user, sendto, msg[(len(self.factory.nickname)+2):].lstrip('!') )
        elif channel == self.factory.nickname:
            self.act( user, sendto, msg )

    def act(self, user, channel, msg):
        print msg
        if msg == 'help':
            self.msg(channel, "Hi %s, I'm %s. I follow %s around." % (user, self.factory.nickname, self.factory.follownick))
        elif msg == 'die':
            self.msg(channel, 'YELP!')
            self.leave(channel)
        elif msg == 'woof':
            self.msg(channel, 'WOOF')
        elif msg == 'meow':
            self.msg(channel, 'MEOW? Do you think I\'m a cat or something... I\'m %s!' % self.factory.nickname)
        elif msg == 'fight':
            self.msg(channel, 'Release the hounds you say?? RAWWR')
        elif msg == 'heel':
            if user != self.factory.follownick:
                self.msg(channel, 'I only heel for %s' % self.factory.follownick)
            else:
                self.msg(channel, 'Yes master :(')
        elif msg == 'quote':
            self.msg(channel, 'YOU WANT A QUOTE?! YOU CAN\'T HANDLE A QUOTE')
        else:
            self.msg(channel, 'I don\'t know what you mean by \'%s\'' % msg)


#    def irc_unknown(self, prefix, command, params):
#        print "%s: %s(%s)" % (prefix, command, params)

    def lineReceived(self, line):
        #print line
        irc.IRCClient.lineReceived(self, line)


class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, nickname='bathound', follownick='batman'):
        self.nickname = nickname
        self.follownick = follownick

    def clientConnectionLost(self, connector, reason):
        print "Connection lost. Reason: %s" % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed. Reason: %s" % reason
        connector.connect()

if __name__ == "__main__":
    reactor.connectTCP('irc', 6667, BotFactory())
    reactor.run()
