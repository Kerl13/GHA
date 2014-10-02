import multiprocessing
from multiprocessing import Queue
from Queue import Empty
from bottle import Bottle, request
from time import sleep
import ircbot
import irclib
from json import loads
import argparse
from sys import argv

parser = argparse.ArgumentParser(description='', prog=argv[0])

parser.add_argument('-gh', '--gh-host', type=str, help='the address where github sends the data')
parser.add_argument('-gp', '--gh-port', type=int, help='the port where github sends the data')

parser.add_argument('-ih', '--irc-host', type=str, help='the irc server\'s address')
parser.add_argument('-ip', '--irc-port', type=int, help='the irc server\'s port')
parser.add_argument('-ic', '--irc-chans', nargs='*', help='the irc channels')
parser.add_argument('-in', '--irc-name', type=str, help='the bot\'s name')

args = parser.parse_args()


################################################################################
class BottleThread(multiprocessing.Process):

    def __init__(self, host, port, queue):
        multiprocessing.Process.__init__(self)
        self.app = Bottle()
        self.host = host
        self.port = port
        self.queue = queue

    def run(self):
        @self.app.route('/', method='POST')
        def index():
            self.queue.put(request.body.read())
            return 'Data received, thanks ;)'

        try:
            self.app.run(host=self.host, port=self.port, quiet=True)
        except Exception, ex:
            print ex


################################################################################
class PrinterBot(ircbot.SingleServerIRCBot):

    def __init__(self, server, port, chans, name, queue):
        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], name, name, 10)
        self.chans = chans
        self.name = name
        self.queue = queue

    def on_welcome(self, serv, ev):
        self.serv = serv
        for chan in self.chans:
            self.serv.join(chan)
        self.routine()

    def on_pubmsg(self, serv, ev):
        if args.irc_name in ev.arguments()[0]:
            self.prnt('I am an announcer bot for github.\nI\'m waiting for webhooks on %s:%d, and printing them on %s:%d on channels %s.\nUse me please ;)' % (args.gh_host, args.gh_port, args.irc_host, args.irc_port, ', '.join(args.irc_chans)), [ev.target()])

    def on_privmsg(self, serv, ev):
        if args.irc_name in ev.arguments()[0]:
            self.prnt('I am an announcer bot for github.\nI\'m waiting for webhooks on %s:%d, and printing them on %s:%d on channels %s.\nUse me please ;)' % (args.gh_host, args.gh_port, args.irc_host, args.irc_port, ', '.join(args.irc_chans)), [ev.source()])

    def prnt(self, text, chans=None):
        if chans == None: chans = self.chans
        for chan in chans:
            for line in text.split('\n'):
                self.serv.privmsg(chan, line)

    def routine(self):
        try:
            a = self.queue.get_nowait()
            data = loads(a)
            text = ''
            ###
            if 'pusher' in data:
                text += '%c%d%s%c pushed ' % (3, 11, data['pusher']['name'], 3)
                if len(data['commits']) == 1: text += '1 commit '
                else: text += '%d commits ' % len(data['commits'])
                text += 'to %c%d%s%c/' % (3, 13, data['repository']['full_name'], 3)
                text += '%c%d%s%c\n' % (3, 5, data['ref'].split('/').pop(), 3)
                for commit in data['commits']:
                    text += '[%c%d%s%c] ' % (3, 14, commit['id'][:7], 3)
                    text += '%c%s%c: ' % (2, commit['author']['name'], 2)
                    text += '%s\n' % commit['message'].split('\n')[0]

            elif 'zen' in data:
                text += '%c%d%s%c added ' % (3, 11, data['sender']['login'], 3)
                text += 'a webhook for %c%d%s%c' % (3, 13, data['repository']['full_name'], 3)

            elif 'issue' in data:
                if data['action'] == 'opened': # Creation d'une issue
                    text += '%c%d%s%c opened ' % (3, 11, data['sender']['login'], 3)
                    text += 'the issue %c%d#%d%c ' % (3, 14, data['issue']['number'], 3)
                    text += 'on %c%d%s%c: ' % (3, 13, data['repository']['full_name'], 3)
                    text += '[%c%d%s%c] ' % (3, 5, data['issue']['title'], 3)
                    text += data['issue']['body'].split('\n')[0] + '\n'

                elif data['action'] == 'created': # Reponse a une issue
                    text += '%c%d%s%c answered ' % (3, 11, data['sender']['login'], 3)
                    text += 'to the issue %c%d#%d%c ' % (3, 14, data['issue']['number'], 3)
                    text += 'on %c%d%s%c: ' % (3, 13, data['repository']['full_name'], 3)
                    text += data['comment']['body'].split('\n')[0] + '\n'

                elif data['action'] == 'labeled': # Ajout de labels
                    text += '%c%d%s%c labeled ' % (3, 11, data['sender']['login'], 3)
                    text += 'the issue %c%d#%d%c ' % (3, 14, data['issue']['number'], 3)
                    text += 'on %c%d%s%c: ' % (3, 13, data['repository']['full_name'], 3)
                    text += ', '.join([l['name'] for l in data['issue']['labels']])

                elif data['action'] == 'assigned': # Assignation de quelqu'un
                    text += '%c%d%s%c assigned ' % (3, 11, data['sender']['login'], 3)
                    text += '%c%d%s%c ' % (3, 5, data['issue']['assignee']['login'], 3)
                    text += 'on the issue %c%d#%d%c ' % (3, 14, data['issue']['number'], 3)
                    text += 'on %c%d%s%c' % (3, 13, data['repository']['full_name'], 3)

                elif data['action'] == 'closed': # Fermeture
                    text += '%c%d%s%c closed ' % (3, 11, data['sender']['login'], 3)
                    text += 'the issue %c%d#%d%c ' % (3, 14, data['issue']['number'], 3)
                    text += 'on %c%d%s%c' % (3, 13, data['repository']['full_name'], 3)

                elif data['action'] == 'reopened': # Reouverture
                    text += '%c%d%s%c reopened ' % (3, 11, data['sender']['login'], 3)
                    text += 'the issue %c%d#%d%c ' % (3, 14, data['issue']['number'], 3)
                    text += 'on %c%d%s%c' % (3, 13, data['repository']['full_name'], 3)

                else:
                    text += 'I received some data on an issue, that i\'m not able to parse :('
                    text += ' [%s]' % data['action']

            else:
                text = 'I just received some data that i\'m not able to parse :('
            ###
            self.prnt(text)
        except Empty:
            pass
        irclib.ServerConnection.execute_delayed(self.serv, 1, self.routine)


################################################################################

queue = Queue()
BottleThread(args.gh_host, args.gh_port, queue).start()

pb = PrinterBot(args.irc_host, args.irc_port, args.irc_chans, args.irc_name, queue).start()

