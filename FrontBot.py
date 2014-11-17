#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import *

import ircbot
import irclib
from multiprocessing import Process, Queue
from Queue import Empty
from traceback import format_exc


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
        V.prnt('[FrontBot %s] %s' % (self.name, string), level)


    def __init__(self, server = 'localhost', port = 6667, chans = [], name = 'FrontBot',
                 input_queues = [], output_queues = []):
        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], name, name, 10)
        self.chans = chans
        self.name = name
        self.input_queues = input_queues
        self.output_queues = output_queues
        self._vprnt('init on %s/%d : %s' % (server, port, ', '.join(chans)), V.DEBUG)


    def on_welcome(self, serv, ev):
        self._vprnt('welcomed', V.DEBUG)
        self.serv = serv
        self.chan_queues = {}
        for chan in self.chans:
            self.serv.join(chan)
        for input_queue in self.input_queues:
            self._check_queue(input_queue)


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
            line = self.chan_queues[chan].get_nowait()
            self.serv.privmsg(chan, line)
        except Empty:
            pass
        except:
            self._vprnt('_prnt: Uncaught exception', V.ERROR)
            for line in format_exc().split('\n'):
                self._vprnt(line, V.ERROR)
        irclib.ServerConnection.execute_delayed(self.serv, TIME_BETWEEN_MESSAGES,
                                                self._prnt, (chan,))


    def prnt(self, message, chans=None):
        '''
        Prints the given message on the given chans.
        @param message: The message to print. Can be multilined.
        @param chans: The chan list where to print. If None is given, all chans are used.
        '''
        if chans == None:
            chans = self.chans
        self._vprnt('prnt on %s : %s' % (', '.join(chans), message), V.DEBUG)
        for chan in chans:
            if chan not in self.chan_queues:
                self.chan_queues[chan] = Queue()
                self._prnt(chan)
            for line in message.split('\n'):
                self.chan_queues[chan].put(line)


    def add_chan(self, chan):
        '''
        Adds the chan to the chan list, creates its queue and join it.
        Prints a V.WARNING level message if chan is already in the list.
        @param chan: The chan to add.
        '''
        self._vprnt('adding chan %s' % (chan,), V.DEBUG)
        if chan not in self.chans:
            self.serv.join(chan)
            self.chan_queues[chan] = Queue()
            self._prnt(chan)
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
            getattr(self, e[0])(*e[1])
        except Empty:
            pass
        except:
            self._vprnt('_check_queue: Uncaught exception', V.ERROR)
            for line in format_exc().split('\n'):
                if line:
                    self._vprnt(line, V.ERROR)
        irclib.ServerConnection.execute_delayed(self.serv, TIME_BETWEEN_QUEUE_CHECKS,
                                                self._check_queue, (queue,))



class FrontBotThread(Process):

    '''
    A little Thread class allowing you to run your FrontBot encapsulated in
    a Thread. Create a bot, give him some multiprocessing.Queues in order to
    be able to communicate with hime. Then, create a FrontBotThread with the
    FrontBot as argument.
    If F is your FrontBot, you could simply do something like that:
    FrontBotThread(F).start().
    '''

    def __init__(self, bot):
        Process.__init__(self)
        self.bot = bot

    def run(self):
        self.bot.start()



class Color:

    '''
    A little class for IRC colors.
    '''

    #           = 14
    #           = 15
    #           = 16
    gray        = 17
    blue        = 18
    green       = 19
    orange      = 20
    red         = 21
    purple      = 22
    brown       = 23
    yellow      = 24
    light_green = 25
    #           = 26
    cyan        = 27
    #           = 28
    pink        = 29
        
    bold   = 'bold'

    def _colorize(self, color, string):
        if color == 'bold':
            return '%c%s%c' % (2, string, 2)
        else:
            return '%c%d%c%s%c%c' % (3, color, 2, string, 2, 3)

    # Please, I want to do that dynamically =(

    def Red (self, string, bold=True):
        c = self._colorize(self.red, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Purple (self, string, bold=True):
        c = self._colorize(self.purple, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Pink (self, string, bold=True):
        c = self._colorize(self.pink, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Orange (self, string, bold=True):
        c = self._colorize(self.orange, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def LightGreen (self, string, bold=True):
        c = self._colorize(self.light_green, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Green (self, string, bold=True):
        c = self._colorize(self.green, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Gray (self, string, bold=True):
        c = self._colorize(self.gray, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Cyan (self, string, bold=True):
        c = self._colorize(self.cyan, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Brown (self, string, bold=True):
        c = self._colorize(self.brown, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Bold (self, string, bold=True):
        c = self._colorize(self.bold, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

    def Blue (self, string, bold=True):
        c = self._colorize(self.blue, string)
        if not bold:
            c = '%c%s%c' % (2, c, 2)
        return c

C = Color()
