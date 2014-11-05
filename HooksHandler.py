#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import *

from multiprocessing import Process, Queue
from Queue import Empty
from Bottle import Bottle, request, redirect


class HooksHandlerThread(Process):

    def __init__(self, host = 'localhost', port = 80, short_urls = None, queues = []):
        Process.__init__(self)
        self.host = host
        self.port = port
        self.short_urls = short_urls
        self.queues = queues
        self.app = Bottle()
        V.prnt('[HooksHandler] ignited on %s/%s' % (host, port), V.DEBUG)

    def run(self):
        @self.app.route('/', method='POST')
        def index():
            V.prnt('[HooksHandler] Received request', V.DEBUG)
            headers_list = request.headers.items()
            headers_dict = {}
            for key, value in headers_list:
                headers_dict[key] = value
            body = request.body.read()
            for queue in self.queues:
                queue.put((headers_dict, body))
            return ''

        @self.app.route('/<i>')
        def shorturl(i):
            url = self.short_urls.short_to_url(i, False)
            redirect(url)

        try:
            self.app.run(host=self.host, port=self.port, quiet=True)
        except Exception, ex:
            V.prnt('[HooksHandler] Error while starting server: '+str(ex), V.ERROR)

