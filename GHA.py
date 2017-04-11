#!/usr/bin/env python3

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

# Regular python imports
import argparse
import logging
import json
from sys import argv
from os import getpid
from multiprocessing import Process, Queue
from traceback import format_exc

# GHA specific imports
from parsing.gitlab import parse as gitlab_parse
from parsing.github import parse as github_parse

from entrypoints.web import HooksHandlerThread

from outputs.irc import FrontBot, FrontBotThread


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
            self.text_queue,
            self.config.irc_host,
            self.config.irc_port,
            self.config.irc_chans,
            self.config.irc_name
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
            hook = json.loads(body)
            try:
                git_obj = None
                if 'X-GitHub-Event' in headers.keys():
                    git_obj = github_parse(headers, hook)
                else:
                    git_obj = gitlab_parse(hook)
                if git_obj is not None:
                    self.text_queue.put((
                        "prnt",
                        {"message": git_obj.render_irccolors()}
                    ))

            except:
                if self.config.report_errors:
                    for line in format_exc().split('\n'):
                        if line:
                            self.text_queue.put((
                                "prnt",
                                {
                                    "message": line,
                                    "chans": [self.config.report_errors]
                                }
                            ))


if __name__ == "__main__":
    # ---
    # Parsing command line arguments
    # ---

    DESCRIPTION = """Github Announcer"""

    parser = argparse.ArgumentParser(description=DESCRIPTION, prog=argv[0])

    parser.add_argument('-lh', '--listen-host',
                        type=str,
                        help='the address where GHA will be listening')

    parser.add_argument('-lp', '--listen-port',
                        type=int,
                        help='the port where GHA will be listening')

    parser.add_argument('-ih', '--irc-host',
                        type=str,
                        help="the irc server\'s address")

    parser.add_argument('-ip', '--irc-port',
                        type=int,
                        help="the irc server's port")

    parser.add_argument('-ic', '--irc-chans',
                        nargs='*',
                        help='the irc channels')

    parser.add_argument('-in', '--irc-name',
                        type=str,
                        help="the bot's name")

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

    parser.add_argument("-v", "--verbosity",
                        type=int,
                        default=1,
                        help="verbosity level")

    config = parser.parse_args()

    # ---
    # Setting up the logger configuration
    # ---

    log_level = logging.WARN
    if 0 <= config.verbosity <= 3:
        levels = [logging.CRITICAL, logging.WARN, logging.INFO, logging.DEBUG]
        log_levels = levels[config.verbosity]
    else:
        logging.error("Invalid verbosity level: {:d}.\nMaximum verbosity: 3"
                      .format(config.verbosity))
        exit(1)

    logging.basicConfig(format='%(asctime)s | %(levelname)s | %(filename)s '
                               'line %(lineno)s | %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', level=log_levels)

    if config.import_arguments:
        try:
            file_config = None
            with open(config.import_arguments, "r") as file:
                file_config = json.load(file)
            # The command line arguments have the priority:
            # If an argument is specified both in the command line and in a
            # config file, we pick the command line's one
            for arg in file_config:
                if hasattr(config, arg):
                    if not getattr(config, arg):
                        setattr(config, arg, file_config[arg])
                else:
                    setattr(config, arg, file_config[arg])
        except FileNotFoundError:
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

    logging.info("Main thread's pid: {:d}".format(getpid()))
    if config.write_pid:
        open(config.write_pid, 'w').close()  # Shrink size to 0
        logging.debug(
            "Writing main thread's pid in `{:s}`."
            .format(config.write_pid)
        )
        with open(config.write_pid, 'a') as file:
            file.write("{:d\n".format(getpid()))

    if config.export_arguments:
        args = {
            arg: value
            for arg, value in vars(config).items()
            if arg not in ['import_arguments', 'export_arguments']
        }
        with open(config.export_arguments, 'w+') as file:
            json.dump(args, file, indent=4)
        exit(0)

    gha = GHA(config)
    gha.start()
    gha.join()
