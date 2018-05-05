from kazoo.client import KazooClient
import logging


class DistributedLock:
    def __init__(self, hosts, logger=None):
        self.client = KazooClient(hosts=hosts, logger=logger)

    def ensure_path(self, path):
        self.client.start()
        self.client.ensure_path(path)
        self.client.stop()

    def try_lock(self, path):
        try:
            self.client.start()
            self.client.create(path, ephemeral=True)
            return True
        except:
            logging.exception("try lock exception. path: {}".format(path))
            return False

    def try_unlock(self, path):
        try:
            self.client.delete(path)
            self.client.stop()
            return True
        except:
            logging.exception("try unlock exception. path: {}".format(path))
            return False
