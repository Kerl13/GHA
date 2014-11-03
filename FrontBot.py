#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import V
V = V(V.DEBUG)   # A CHANGER PLUS TARD

import ircbot
import irclib
#from multiprocessing import Queue
from Queue import Empty


HELP_MESSAGE = '''I am a PrinterBot writen in Python with IRCBot.
I provide a PrinterBot.prnt method allowing some other python scripts
to print nicely on IRC.'''


'''
Time between messages in seconds.
The bot will avoid to spam the chans in which he's writing, because it could
make him kicked, which is not the aim ;)
'''
TIME_BETWEEN_MESSAGES = 1


'''
Time between queue checks in seconds.
The bot has to be present on IRC, so we can't just wait for something to come
into the queue.
So it'll only check queue regularly, and you can here define the time between
these checks.
'''
TIME_BETWEEN_QUEUE_CHECKS  = 0.1


class FrontBot(ircbot.SingleServerIRCBot):

    '''
    This IRC bot's job is only to be an interface between IRC and a python script.
    It communicates through self for multiprocessing queues, so that you can safely
    use threads.
    Since the IRC bot is busy communicating with the IRC server, you can't just
    call one of his methods. You have to put a dictionnary {'method', 'args'} in
    (one of) the input queues, and the bot will do the job.
    '''

    def _vprnt(self, string, level):
        V.prnt('[PrinterBot %s] %s' % (self.name, string), level)


    def __init__(self, server='localhost', port=6667, chans=[], name='FrontBot'):
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
            pass
            # PARTIR DU CANAL
            # SUPPRIMER L'ENTRÉE DU DICTIONNAIRE
        else:
            self._vprnt('chan %s is not in chan list (%s)' \
                        % (chan, ', '.join(self.chans)),
                        V.WARNING)


    def _check_queue(self, queue):
        try:
            e = queue.get_nowait()
            self.getattr(e['method'])(e['args'])
        except Empty:
            pass
        except:
            self._vprnt('_check_queue: Uncaught exception', V.ERROR) # AJOUTER DES DETAILS
        irclib.ServerConnection.execute_delayed(self.serv, TIME_BETWEEN_QUEUE_CHECKS,
                                                self._check_queue, (queue,))


