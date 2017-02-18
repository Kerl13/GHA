###############################################################################
#                                                                             #
#                                  FrontBot.py                                #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#                                                       –– Poul-Henning Kamp  #
#                                                                             #
###############################################################################

from irc.bot import SingleServerIRCBot
import logging
from multiprocessing import Process
from queue import Empty

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
TIME_BETWEEN_QUEUE_CHECKS = 0.1


class FrontBot(SingleServerIRCBot):
    """
    This IRC bot's job is only to be an interface between IRC and a python
    script.  It communicates through self for multiprocessing queues, so that
    you can safely use threads. Since the IRC bot is busy communicating with
    the IRC server, you can't just call one of his methods. You have to put a
    dictionnary {'method', 'args'} in (one of) the input queues, and the bot
    will do the job.
    """

    def __init__(self, input_queue, server='localhost', port=6667, chans=[],
                 name='FrontBot'):
        super().__init__([(server, port)], name, name, 10)
        self.chans = chans
        self.name = name
        self.input_queue = input_queue
        logging.info('Init on %s/%s : %s', server, port, ', '.join(chans))

    def on_welcome(self, connection, event):
        logging.info('Welcomed')
        for chan in self.chans:
            connection.join(chan)
        connection.execute_every(
            TIME_BETWEEN_MESSAGES,
            self._check_queue
        )

    def _check_queue(self):
        try:
            (meth, kwargs) = self.input_queue.get_nowait()
            method = getattr(self, meth)
            method(**kwargs)
        except Empty:
            pass

    def on_pubmsg(self, connection, event):
        logging.debug(
            'pubmsg {}/{}: {}'
            .format(
                event.target,
                event.source.nick,
                event.arguments[0]
            )
        )
        if event.arguments[0] == "{}: help".format(self.name):
            self.prnt(
                message=HELP_MESSAGE,
                chans=[event.target]
            )

    def on_privmsg(self, connection, event):
        logging.debug(
            "privmsg {}: {}",
            event.source.nick,
            event.arguments[0]
        )
        if event.arguments[0] == "{}: help".format(self.name):
            self.prnt(
                message=HELP_MESSAGE,
                chans=[event.source.nick]
            )

    def prnt(self, message, chans=None):
        '''
        Prints the given message on the given chans.
        @param message: The message to print. Can be multilined.
        @param chans: The chan list where to print. If None is given, all chans
        are used.
        '''
        if chans is None:
            chans = self.chans
        if not isinstance(chans, list):
            chans = [chans]
        logging.debug('prnt on %s : %s', ', '.join(chans), message)
        lines = message.split('\n')
        for chan in chans:
            for line in lines:
                self.connection.privmsg(chan, line)


class FrontBotThread(Process):

    '''
    A little Thread class allowing you to run your FrontBot encapsulated in
    a Thread. Create a bot, give him some multiprocessing.Queues in order to
    be able to communicate with him. Then, create a FrontBotThread with the
    FrontBot as argument.
    If F is your FrontBot, you could simply do something like that:
    FrontBotThread(F).start().
    '''

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def run(self):
        self.bot.start()
