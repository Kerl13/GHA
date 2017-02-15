#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
#                                HooksHandler.py                              #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#  –– Poul-Henning Kamp                                                       #
#                                                                             #
###############################################################################

import logging
from multiprocessing import Process
from Bottle import Bottle, request


class HooksHandlerThread(Process):

    def __init__(self, host='localhost', port=80, queues=[]):
        Process.__init__(self)
        self.host = host
        self.port = port
        self.queues = queues
        self.app = Bottle()
        logging.info('Ignited on %s/%s', host, port)

    def run(self):
        @self.app.route('/', method='POST')
        def index():
            logging.debug('Received request')
            headers_list = request.headers.items()
            headers_dict = {}
            for key, value in headers_list:
                headers_dict[key] = value
            body = request.body.read()
            for queue in self.queues:
                queue.put((headers_dict, body))
            return ''

        try:
            self.app.run(host=self.host, port=self.port, quiet=True)
        except Exception as ex:
            logging.critical('Error while starting server: %s', str(ex))
