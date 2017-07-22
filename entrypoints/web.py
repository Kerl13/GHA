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
from socketserver import UnixStreamServer

# This one is the class Queue whereas multiprocessing.Queue is just a function…
# Yeah this python developers have a great sense of humour
from multiprocessing.queues import Queue


# ---
# The web server
# ---

class SimplePOSTHandler(BaseHTTPRequestHandler):
    def parse_request(self):
        """
        If no client address is provided, look for the X-Real-IP header
        """
        success = super().parse_request()
        if success:
            if not self.client_address and "X-Real-IP" in self.headers:
                self.client_address = (self.headers.get("X-Real-IP"), None)
        return success

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


class GHAUnixStreamServer(UnixStreamServer):
    def __init__(self, hooks_queue, *args, **kwargs):
        assert isinstance(hooks_queue, Queue)
        super().__init__(*args, **kwargs)
        self.hooks_queue = hooks_queue


class GHAHTTPServer(HTTPServer):
    def __init__(self, hooks_queue, *args, **kwargs):
        assert isinstance(hooks_queue, Queue)
        super().__init__(*args, **kwargs)
        self.hooks_queue = hooks_queue


# ---
# The handler thread
# ---

class HooksHandlerThread(Process):
    def __init__(self, queue, type, bind):
        assert isinstance(queue, Queue)
        super().__init__()
        self.queue = queue
        self._init_app(type, bind)

    def _init_app(self, type, bind):
        if type == "http":
            host, port = bind
            self.app = GHAHTTPServer(
                self.queue, (host, port), SimplePOSTHandler
            )
            logging.info("Ignited on %s:%d", host, port)

        elif type == "unix":
            self.app = GHAUnixStreamServer(self.queue, bind, SimplePOSTHandler)
            logging.info("Ignited on unix:/%s", bind)

        else:
            logging.critical("Unknown server type: %s. Aborting.", type)
            exit(1)

    def run(self):
        try:
            self.app.serve_forever()
        except Exception as ex:
            logging.critical('Error while starting server: %s', str(ex))
