#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import V
V = V()

import argparse
from sys import argv


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
        ARGS = loads(open(ARG.import_arguments).read())
    except IOError:
        V.prnt('The file %s were not found' % (ARGS.import_arguments),
               V.ERROR)
        exit(1)

if ARGS.export_arguments:
    open(ARGS.export_arguments, 'w+').write(dumps(ARGS.export_arguments))
    exit(0)

if not ARGS.gh_host:
    V.prnt('No GitHub Host given. Using localhost.', V.WARNING)
    ARGS.gh_host = 'localhost'

if not 'gh-port' in ARGS:
    V.prnt('No GitHub Port given. Using 80.', V.WARNING)
    ARGS.gh_port = 80

if not 'irc-host' in ARGS:
    V.prnt('No IRC Host given. Using localhost.', V.WARNING)
    ARGS.irc_host = 'localhost'

if not 'irc-port' in ARGS:
    V.prnt('No IRC Port given. Using 6667.', V.WARNING)
    ARGS.irc_port = 6667

if not 'irc-chans' in ARGS:
    V.prnt('No IRC Chans given.', V.WARNING)

if not 'irc-name' in ARGS:
    V.prnt('No IRC Name given. Using GHA.', V.WARNING)
    ARGS.irc_name = 'GHA'


V.prnt('OK.')
print 'OK...'
exit(0)
