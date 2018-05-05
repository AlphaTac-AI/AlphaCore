import logging
from multiprocessing import Pool
from mlx_server import server
from mlx_message import message_manager as mm
from mlx_utility import config_manager as cm
from mlx_exception.exception_handler.dingding_exception_handler import DingdingExceptionHandler
import time


class MessageServer(server.Server):
    def __init__(self):
        super().__init__()
        self.stop_server = False
        self.queue = None
        self.setup_message()
        self.idle_seconds = None
        self.stop_wait_seconds = None
        self.processes = None
        self.setup_idle_seconds()
        self.exception_handlers = []
        self.setup_exception_handlers()

    def setup_message(self):
        mc = cm.config['queue_server']
        mm.setup_message(mc['host'], mc['access_id'], mc['access_key'], logger=logging.getLogger('elogger'))
        self.queue = mm.get_queue(mc['name'])
        logging.info("message setup finished")

    def setup_idle_seconds(self):
        # if no message consumed, idle for a while
        self.idle_seconds = cm.config['queue_server'].get('idle_seconds', 10)
        self.stop_wait_seconds = cm.config['queue_server'].get('stop_wait_seconds', 10)
        self.processes = cm.config['queue_server'].get('processes', 1)

    def setup_exception_handlers(self):
        if 'dingding' in cm.config:
            self.exception_handlers.append(
                DingdingExceptionHandler(cm.config['dingding']['robots'], cm.config.get('env')))

    def run(self):
        while not self.stop_server:
            try:
                success, msg_dict = self.queue.consume_message()
                if not success:
                    time.sleep(self.idle_seconds)
                    continue
                self.handle_msg(msg_dict)
            except Exception as ex:
                logging.exception("exception occurred!")
                self.handle_exception(ex)

    def handle_msg(self, msg_dict):
        pass

    def handle_exception(self, ex):
        logging.exception("exception occurred!")
        try:
            for exhandler in self.exception_handlers:
                exhandler.handle(ex)
        except:
            logging.exception("exception occurred while handling exception -_-!")

    def stop(self):
        self.stop_server = True
