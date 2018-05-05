import logging

from utility import server
from flask import Flask
from gevent.wsgi import WSGIServer


class RestServer(server.Server):
    def __init__(self, ip,port):
        super().__init__()
        self.app = None
        self.setup_app()
        self.rest_server = None
        self.setup_rest_server(ip, port)

    def run(self):
        self.rest_server.serve_forever()

    def stop(self):
        self.rest_server.stop(timeout=10)  # maximum timeout waiting for the client connections to close

    def setup_app(self):
        self.app = Flask(__name__)
        # set flask app log handlers
        self.app.logger.handlers = []
        log_handlers = logging.getLogger().handlers
        for lh in log_handlers:
            self.app.logger.addHandler(lh)

    def setup_rest_server(self, ip, port):
        self.rest_server = WSGIServer(('', port), self.app,
                                      log=logging.getLogger('aflogger'),
                                      error_log=logging.getLogger('flogger'))

    def register_router(self, router):
        self.app.register_blueprint(router)
        return self

    def register_routers(self, *routers):
        for r in routers:
            self.register_router(r)
