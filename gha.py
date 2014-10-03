import multiprocessing
from multiprocessing import Queue
from Queue import Empty
from bottle import Bottle, request
from time import sleep
import ircbot
import irclib
from json import dumps, loads
import argparse
from sys import argv

parser = argparse.ArgumentParser(description='', prog=argv[0])

parser.add_argument('-gh', '--gh-host', type=str, help='the address where github sends the data')
parser.add_argument('-gp', '--gh-port', type=int, help='the port where github sends the data')

parser.add_argument('-ih', '--irc-host', type=str, help='the irc server\'s address')
parser.add_argument('-ip', '--irc-port', type=int, help='the irc server\'s port')
parser.add_argument('-ic', '--irc-chans', nargs='*', help='the irc channels')
parser.add_argument('-in', '--irc-name', type=str, help='the bot\'s name')

parser.add_argument('-ea', '--export-arguments', metavar='FILE', type=str, help='export arguments in the given file')
parser.add_argument('-ia', '--import-arguments', metavar='FILE', type=str, help='import arguments from the given file')

args = parser.parse_args()

class Arguments:
    GH_HOST = None
    GH_PORT = None
    IRC_HOST = None
    IRC_PORT = None
    IRC_CHANS = None
    IRC_NAME = None
    def to_dictionnary(self):
        d = {}
        if self.GH_HOST: d['gh-host'] = self.GH_HOST
        if self.GH_PORT: d['gh-port'] = self.GH_PORT
        if self.IRC_HOST: d['irc-host'] = self.IRC_HOST
        if self.IRC_PORT: d['irc-port'] = self.IRC_PORT
        if self.IRC_CHANS: d['irc-chans'] = self.IRC_CHANS
        if self.IRC_NAME: d['irc-name'] = self.IRC_NAME
        return d
    def from_dictionnary(self, d):
        if 'gh-host' in d: self.GH_HOST = d['gh-host']
        if 'gh-port' in d: self.GH_PORT = d['gh-port']
        if 'irc-host' in d: self.IRC_HOST = d['irc-host']
        if 'irc-port' in d: self.IRC_PORT = d['irc-port']
        if 'irc-chans' in d: self.IRC_CHANS = d['irc-chans']
        if 'irc-name' in d: self.IRC_NAME = d['irc-name']
    def give_errors(self):
        text = ''
        if not self.GH_HOST: text += 'You need to give a gh-host.\n'
        if not self.GH_PORT: text += 'You need to give a gh-port.\n'
        if not self.IRC_HOST: text += 'You need to give a irc-host.\n'
        if not self.IRC_PORT: text += 'You need to give a irc-port.\n'
        if not self.IRC_CHANS: text += 'You need to give a irc-chans.\n'
        if not self.IRC_NAME: text += 'You need to give a irc-name.\n'
        return text

ARGS = Arguments()

if args.import_arguments:
    try:
        d = loads(open(args.import_arguments).read())
        ARGS.from_dictionnary(d)
    except IOError:
        print 'Error: the file %s doesn\'t exist' % args.import_arguments
        exit(1)

if args.gh_host: ARGS.GH_HOST = args.gh_host
if args.gh_port: ARGS.GH_PORT = args.gh_port
if args.irc_host: ARGS.IRC_HOST = args.irc_host
if args.irc_port: ARGS.IRC_PORT = args.irc_port
if args.irc_chans: ARGS.IRC_CHANS = args.irc_chans
if args.irc_name: ARGS.IRC_NAME = args.irc_name

if args.export_arguments:
    open(args.export_arguments, 'w+').write(dumps(ARGS.to_dictionnary()))
    exit(0)

errors = ARGS.give_errors()
if errors:
    print errors[:len(errors)-1]
    exit(1)



################################################################################
colorize = lambda c, s: '%c%c%d%s%c%c' % (2, 3, c, s, 3, 2)
col = colorize
gray   = 14
pink   = 13
blue   = 12
cyan   = 11
green  = 9
yellow = 7
red    = 5
black  = 1
white  = 15


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
            self.queue.put((request.headers.get('X-Github-Event'),
                            request.body.read()))
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
        if ev.arguments()[0] == ARGS.IRC_NAME+': help':
            self.prnt('I am an announcer bot for github.\nI\'m waiting for webhooks on %s:%d, and printing them on %s:%d on channels %s.\nUse me please ;)' % (ARGS.GH_HOST, ARGS.GH_PORT, ARGS.IRC_HOST, ARGS.IRC_PORT, ', '.join(ARGS.IRC_CHANS)), [ev.target()])

    def on_privmsg(self, serv, ev):
        if ev.arguments()[0] == ARGS.IRC_NAME+': help':
            self.prnt('I am an announcer bot for github.\nI\'m waiting for webhooks on %s:%d, and printing them on %s:%d on channels %s.\nUse me please ;)' % (ARGS.GH_HOST, ARGS.GH_PORT, ARGS.IRC_HOST, ARGS.IRC_PORT, ', '.join(ARGS.IRC_CHANS)), [ev.source()])

    def prnt(self, text, chans=None):
        if chans == None: chans = self.chans
        for chan in chans:
            for line in text.split('\n'):
                self.serv.privmsg(chan, line)

    def routine(self):
        try:
            event, data = self.queue.get_nowait()
            data = loads(data)
            # LA COLORATION POURRAIT SE FAIRE ICI, A MEME data...
            text = ''
            ###
            if event == 'push':
                if len(data['commits']) > 0:
                    text += '%s pushed ' % data['pusher']['name']
                    if len(data['commits']) == 1: text += '1 commit '
                    else: text += '%d commits ' % len(data['commits'])
                    text += 'to %s/' % data['repository']['full_name']
                    text += '%s\n' % data['ref'].split('/').pop()
                    for commit in data['commits']:
                        text += '[%s] ' % commit['id'][:7]
                        text += '%s: ' % commit['author']['name']
                        text += '%s\n' % commit['message'].split('\n')[0]

            elif event == 'create':
                if data['ref_type'] == 'branch':
                    text += '%s created ' % data['sender']['login']
                    text += 'the branch %s ' % data['ref']
                    text += 'on %s' % data['repository']['full_name']
                else:
                    text += 'Not implemented. event=create, ref_type='+data['ref_type']

            elif event == 'delete':
                if data['ref_type'] == 'branch':
                    text += '%s deleted ' % data['sender']['login']
                    text += 'the branch %s ' % data['ref']
                    text += 'on %s' % data['repository']['full_name']
                else:
                    text += 'Not implemented. event=delete, ref_type='+data['ref_type']

            elif event == 'commit_comment':
                text += '%s commented ' % data['sender']['login']
                text += 'the commit %s ' % data['comment']['commit_id'][:7]
                text += 'on %s: ' % data['repository']['full_name']
                text += data['comment']['body'].split('\n')[0]

            elif 'zen' in data:
                text += '%s added ' % data['sender']['login']
                text += 'a webhook for %s' % data['repository']['full_name']

            elif 'issue' in data:
                if data['action'] == 'opened': # Creation d'une issue
                    text += '%s opened ' % data['sender']['login']
                    text += 'the issue #%d ' % data['issue']['number']
                    text += 'on %s: ' % data['repository']['full_name']
                    text += data['issue']['title']

                elif data['action'] == 'created': # Reponse a une issue
                    text += '%s answered ' % data['sender']['login']
                    text += 'to the issue #%d ' % data['issue']['number']
                    text += 'on %s' % data['repository']['full_name']

                elif data['action'] == 'labeled': # Ajout de labels
                    text += '%s labeled ' % data['sender']['login']
                    text += 'the issue #%d ' % data['issue']['number']
                    text += 'on %s' % data['repository']['full_name']

                elif data['action'] == 'assigned': # Assignation de quelqu'un
                    text += '%s assigned ' % data['sender']['login']
                    text += '%s ' % data['issue']['assignee']['login']
                    text += 'on the issue #%d ' % data['issue']['number']
                    text += 'on %s' % data['repository']['full_name']

                elif data['action'] == 'closed': # Fermeture
                    text += '%s closed ' % data['sender']['login']
                    text += 'the issue #%d ' % data['issue']['number']
                    text += 'on %s' % data['repository']['full_name']

                elif data['action'] == 'reopened': # Reouverture
                    text += '%s reopened ' % data['sender']['login']
                    text += 'the issue %c%d#%d%c ' % data['issue']['number']
                    text += 'on %s' % data['repository']['full_name']

                else:
                    text += 'I received some data on an issue, that i\'m not able to parse :('
                    text += ' [%s]' % data['action']

            else:
                text = 'I received a %s event, and i\'m not able to parse it :(' % event
            ###
            self.prnt(text)
        except Empty:
            pass
        irclib.ServerConnection.execute_delayed(self.serv, 1, self.routine)


################################################################################

queue = Queue()
BottleThread(ARGS.GH_HOST, ARGS.GH_PORT, queue).start()

pb = PrinterBot(ARGS.IRC_HOST, ARGS.IRC_PORT, ARGS.IRC_CHANS, ARGS.IRC_NAME, queue).start()

