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
from http.server import HTTPServer, BaseHTTPRequestHandler


# ---
# The web server
# ---

class SimplePOSTHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle git{lab,hub}'s POST requests.
        """
        # Fetching data
        content_length = int(self.headers.get("Content-Length"))
        body = self.rfile.read(content_length).decode("utf-8")
        # Responding to server
        self.send_response(200, message="OK")
        self.end_headers()
        # Feeding the hooks queue
        self.server.hooks_queue.put((self.headers, body))


class MyHTTPServer(HTTPServer):
    """
    This server class has also two queues to allow it to communicate with other
    threads.
    """
    def __init__(self, server_address, handler_cls, hooks_queue):
        self.hooks_queue = hooks_queue
        super().__init__(server_address, handler_cls)


# ---
# The handler thread
# ---

class HooksHandlerThread(Process):

    def __init__(self, queue, host='localhost', port=80):
        super().__init__()
        self.host = host
        self.port = port
        self.queue = queue
        self.app = MyHTTPServer((host, port), SimplePOSTHandler, queue)
        logging.info('Ignited on %s:%s', host, port)

    def run(self):
        try:
            self.app.serve_forever()
        except Exception as ex:
            logging.critical('Error while starting server: %s', str(ex))
