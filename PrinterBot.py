#!/usr/bin/env python
# -*- coding: utf-8 -*-

import V
import ircbot
from Queue import Queue, Empty


HELP_MESSAGE = '''I am a PrinterBot writen in Python with IRCBot.
I provide a PrinterBot.prnt method allowing some other python scripts
to print nicely on IRC.'''


'''
Time between messages in seconds.
The bot will avoid to spam the chans in which he's writing, because it could
make him kicked, which is not the aim ;)
'''
TIME_BETWEEN_MESSAGES = 1


class PrinterBot(ircbot.SingleServerIRCBot):

    '''
    An IRC bot whose job is to print messages on IRC.
    You just need to init this bot, and to start it.
    After this, you'll have access to a PrinterBot.prnt method allowing
    you to print messages.
    '''

    def _vprnt(self, string, level):
        V.prnt('[PrinterBot %s]' % (self.name, string), level)


    def __init__(self, server, port, chans, name):
        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], name, name, 10)
        self.chans = chans
        self.name = name
        self._vprnt('init on %s/%d : %s' % (server, port, ', '.join(chans)), V.DEBUG)


    def on_welcome(self, serv, ev):
        self._vprnt('welcomed' % (self.name,), V.DEBUG)
        self.serv = serv
        self.queues = {}
        for chan in self.chans:
            self.serv.join(chan)
            self.queues[chan] = Queue()
        self.routine()


    def on_pubmsg(self, serv, ev):
        self._vprnt('pubmsg %s/%s: %s' % (ev.target(), ev.source(), ev.arguments()[0]),
                    V.DEBUG)
        if ev.arguments()[0] == self.name+': help':
            self.prnt(HELP_MESSAGE, ev.target())


    def on_privmsg(self, serv, ev):
        self._vprnt('privmsg %s: %s' % (ev.source(), ev.arguments()[0]), V.DEBUG)
        if ev.arguments()[0] == self.name+': help':
            self.prnt(HELP_MESSAGE, ev.source())


    def _prnt(self, chan):
        try:
            line = self.queues[chan].get_nowait()
            self.serv.privmsg(chan, line)
            irclib.ServerConnection.execute_delayed(self.serv, TIME_BETWEEN_MESSAGES,
                                                    self._prnt, (chan,))
        except Empty:
            pass
        except:
            self._vprnt('_prnt: Uncaught exception', V.ERROR) # AJOUTER DES DETAILS


    def prnt(self, message, chans=None):
        '''
        Prints the given message on the given chans.
        @param message: The message to print. Can be multilined.
        @param chans: The chan list where to print. If None is given, all chans are used.
        '''
        if chans == None:
            chans = self.chans
        for chan in chans:
            empty = self.queues[chan].empty()
            for line in message.split('\n'):
                self.queues[chan].put(line)
            if empty:
                self._prnt(chan)


    def add_chan(self, chan):
        '''
        Adds the chan to the chan list, creates its queue and join it.
        Prints a V.WARNING level message if chan is already in the list.
        @param chan: The chan to add.
        '''
        self._vprnt('adding chan %s' % (chan,), V.DEBUG)
        if chan not in self.chans:
            self.serv.join(chan)
            self.queues[chan] = Queue()
        else:
            self._vprnt('chan %s already in chan list (%s)' \
                        % (chan, ', '.join(self.chans)),
                        V.WARNING)


    def del_chan(self, chan):
        '''
        Deletes the chan from the chan list, deletes its queue and part from it.
        Prints a V.WARNING level message if chan is not in the list.
        @param chan: The chan to delete.
        '''
        self._vprnt('deleting chan %s' % (chan,), V.DEBUG)
        if chan in self.chans:
            # PARTIR DU CANAL
            # SUPPRIMER L'ENTRÉE DU DICTIONNAIRE
        else:
            self._vprnt('chan %s is not in chan list (%s)' \
                        % (chan, ', '.join(self.chans)),
                        V.WARNING)

