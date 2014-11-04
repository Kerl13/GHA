#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import *

import argparse
from sys import argv
from json import loads, dumps

from FrontBot import *
from HooksHandler import *

from GitHubHooks import *


DESCRIPTION = '''GitHub Announcer


'''

parser = argparse.ArgumentParser(description=DESCRIPTION, prog=argv[0])

parser.add_argument('-gh', '--gh-host',
                    type = str,
                    help = 'the address where github sends the data')

parser.add_argument('-gp', '--gh-port',
                    type = int,
                    help = 'the port where github sends the data')

parser.add_argument('-ih', '--irc-host',
                    type = str,
                    help = 'the irc server\'s address')

parser.add_argument('-ip', '--irc-port',
                    type = int,
                    help = 'the irc server\'s port')

parser.add_argument('-ic', '--irc-chans',
                    nargs = '*',
                    help = 'the irc channels')

parser.add_argument('-in', '--irc-name',
                    type = str,
                    help = 'the bot\'s name')

parser.add_argument('-ea', '--export-arguments',
                    metavar='FILE',
                    type = str,
                    help = 'export arguments in the given file')

parser.add_argument('-ia', '--import-arguments',
                    metavar = 'FILE',
                    type = str,
                    help = 'import arguments from the given file')

parser.add_argument('-vl', '--verbose-level',
                    type = str, # rendre plus précis
                    help = 'the verbose level wanted (DEBUG, WARNING, ERROR)')

ARGS = parser.parse_args()

if ARGS.import_arguments:
    try:
        args = loads(open(ARGS.import_arguments).read())
        for arg in [ s for s in dir(ARGS) if s[0] != '_' ]:
            if arg in args and not getattr(ARGS, arg):
                setattr(ARGS, arg, args[arg])
    except IOError:
        V.prnt('The file %s were not found' % (ARGS.import_arguments),
               V.ERROR)
        exit(1)

if not ARGS.verbose_level:
    V.level = V.WARNING
    V.prnt('No verbose level given. Using WARNING.', V.WARNING)
    ARGS.verbose_level = 'WARNING'

if not ARGS.gh_host:
    V.prnt('No GitHub Host given. Using localhost.', V.WARNING)
    ARGS.gh_host = 'localhost'

if not ARGS.gh_port:
    V.prnt('No GitHub Port given. Using 80.', V.WARNING)
    ARGS.gh_port = 80

if not ARGS.irc_host:
    V.prnt('No IRC Host given. Using localhost.', V.WARNING)
    ARGS.irc_host = 'localhost'

if not ARGS.irc_port:
    V.prnt('No IRC Port given. Using 6667.', V.WARNING)
    ARGS.irc_port = 6667

if not ARGS.irc_chans:
    V.prnt('No IRC Chans given.', V.WARNING)
    ARGS.irc_chans = []

if not ARGS.irc_name:
    V.prnt('No IRC Name given. Using GHA.', V.WARNING)
    ARGS.irc_name = 'GHA'

if ARGS.export_arguments:
    args = {}
    for arg in [ s for s in dir(ARGS) if s[0] != '_' ]:
        args[arg] = getattr(ARGS, arg)
    open(ARGS.export_arguments, 'w+').write(dumps(args, indent=4))
    exit(0)



hooks_queue = Queue ()
text_queue = Queue ()

HooksHandlerThread(ARGS.gh_host, ARGS.gh_port, [hooks_queue]).start()

F = FrontBot(ARGS.irc_host, ARGS.irc_port, ARGS.irc_chans, ARGS.irc_name, [text_queue])
FrontBotThread(F).start()

def irc_prnt (message):
    text_queue.put(('prnt', (message, None)))


while True:
    (headers, body) = hooks_queue.get()

    if 'X-Github-Event' in headers.keys():
        text_queue.put(('prnt', (GitHubHooks.handle(headers, body),)))

    else:
        V.prnt('Received invalid request.', V.WARNING)
