#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
#                                    GHA.py                                   #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#                                                       –– Poul-Henning Kamp  #
#                                                                             #
###############################################################################

import argparse
import logging
import json
from sys import argv
from os import getpid
from multiprocessing import Process, Queue
from traceback import format_exc

from FrontBot import FrontBot, FrontBotThread
from HooksHandler import HooksHandlerThread

# from GitHubHooks import *
from parsing.gitlab import parse as gitlab_parse


class GHA(Process):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.hooks_queue = Queue()
        self.text_queue = Queue()

    def start_webserver(self):
        hht = HooksHandlerThread(
            self.hooks_queue,
            self.config.listen_host,
            self.config.listen_port
        )
        hht.start()
        logging.info("HooksHandlerThread's pid: {:d}".format(hht.pid))
        if self.config.write_pid:
            logging.debug(
                "Writing HooksHandlerThread's pid in `{}`."
                .format(self.config.write_pid)
            )
            with open(self.config.write_pid, 'a') as file:
                file.write("{:d}\n".format(hht.pid))

    def start_ircbot(self):
        bot = FrontBot(
            self.config.irc_host,
            self.config.irc_port,
            self.config.irc_chans,
            self.config.irc_name,
            [self.text_queue]
        )
        bot_thread = FrontBotThread(bot)
        bot_thread.start()

        logging.info("FrontBotThread's pid: {:d}".format(bot_thread.pid))
        if self.config.write_pid:
            logging.debug(
                "Writing FrontBotThread's pid in `{}`."
                .format(self.config.write_pid)
            )
            with open(self.config.write_pid, 'a') as file:
                file.write("{:d}\n".format(bot_thread))

    def run(self):
        self.start_webserver()
        self.start_ircbot()
        while True:
            (headers, body) = self.hooks_queue.get()

            try:
                if 'X-Github-Event' in headers.keys():
                    pass
                else:
                    hook = json.loads(body)
                    git_obj = gitlab_parse(hook)
                    self.text_queue.put(('prnt', git_obj.render_irccolors()))

            except:
                if self.config.report_errors:
                    for line in format_exc().split('\n'):
                        if line:
                            self.text_queue.put(
                                ('prnt', (line, [self.config.report_errors]))
                            )


if __name__ == "__main__":
    DESCRIPTION = """Github Announcer"""

    logging.basicConfig(format='%(asctime)s | %(levelname)s | %(filename)s '
                               'line %(lineno)s | %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description=DESCRIPTION, prog=argv[0])

    parser.add_argument('-lh', '--listen-host',
                        type=str,
                        help='the address where GHA will be listening')

    parser.add_argument('-lp', '--listen-port',
                        type=int,
                        help='the port where GHA will be listening')

    parser.add_argument('-ih', '--irc-host',
                        type=str,
                        help='the irc server\'s address')

    parser.add_argument('-ip', '--irc-port',
                        type=int,
                        help='the irc server\'s port')

    parser.add_argument('-ic', '--irc-chans',
                        nargs='*',
                        help='the irc channels')

    parser.add_argument('-in', '--irc-name',
                        type=str,
                        help='the bot\'s name')

    parser.add_argument('-ea', '--export-arguments',
                        metavar='FILE',
                        type=str,
                        help='export arguments in the given file')

    parser.add_argument('-ia', '--import-arguments',
                        metavar='FILE',
                        type=str,  # à rendre plus précis
                        help='import arguments from the given file')

    parser.add_argument('--write-pid',
                        metavar='FILE',
                        type=str,
                        help='write all threads pids in given file')

    parser.add_argument('-re', '--report-errors',
                        metavar='NICK',
                        type=str,
                        help='Report errors to the given person')

    config = parser.parse_args()

    if config.import_arguments:
        try:
            file_config = None
            with open(config.import_arguments, "r") as file:
                file_config = json.load(file)
            for arg in [s for s in dir(config) if s[0] != '_']:
                if arg in file_config and not getattr(config, arg):
                    setattr(config, arg, file_config[arg])
        except IOError:
            logging.error('File %s not found', config.import_arguments)
            exit(1)
        except:
            logging.error('Error while importing arguments from file.')
            for line in format_exc().split('\n'):
                if line:
                    logging.error(line)
            exit(1)

    if not config.listen_host:
        logging.info('No listen host given. Using 0.0.0.0.')
        config.listen_host = '0.0.0.0'

    if not config.listen_port:
        logging.info('No listen port given. Using 80.')
        config.listen_port = 80

    if not config.irc_host:
        logging.info('No IRC host given. Using localhost.')
        config.irc_host = 'localhost'

    if not config.irc_port:
        logging.info('No IRC port given. Using 6667.')
        config.irc_port = 6667

    if not config.irc_chans:
        logging.info('No IRC chans given.')
        config.irc_chans = []

    if not config.irc_name:
        logging.info('No IRC name given. Using GHA.')
        config.irc_name = 'GHA'

    logging.info('Main thread\'s pid: %d' % (getpid(),))
    if config.write_pid:
        open(config.write_pid, 'w').close()  # Shrink size to 0
        logging.debug('Writing main thread\'s pid in `%s`.' % config.write_pid)
        open(config.write_pid, 'a').write(str(getpid()) + '\n')

    if config.export_arguments:
        args = {}
        for arg in [
                s for s in dir(config) if s[0] != '_'
                and s not in ['import_arguments', 'export_arguments']
                ]:
            args[arg] = getattr(config, arg)
        open(config.export_arguments, 'w+').write(json.dumps(args, indent=4))
        exit(0)

    gha = GHA(config)
    gha.start()
    gha.join()
