import logging
from mlx_server import message_server as ms
from mlx_utility import distributed_lock as dl, config_manager as cm
from mlx_database import mongo
from mlx_flow import mbd_flow as mf
import time
from concurrent.futures import ThreadPoolExecutor
from mlx_message import message_manager as mm


class MBDFlowServer(ms.MessageServer):
    def __init__(self, mbd_flows, default_flow=None):
        super().__init__()
        self.mbd_flows = mbd_flows
        self.default_flow = default_flow
        self.mbd_flow_manager = None
        self.setup_mbd_flow_manager()
        self.zk_hosts = None
        self.zk_root_path = None
        self.zk_locker = None
        self.setup_distributed_lock()

    def run(self):
        executor = None
        if self.processes > 1:
            executor = ThreadPoolExecutor(max_workers=self.processes)
        while not self.stop_server:
            try:
                success, msg_dict = self.queue.consume_message()
                if not success:
                    time.sleep(self.idle_seconds)
                    continue

                if executor:
                    mc = cm.config['queue_server']
                    queue = mm.get_queue(mc['name'], True)
                    executor.submit(self.handle_message, msg_dict, queue)
                else:
                    self.handle_message(msg_dict, self.queue)
            except Exception as ex:
                self.handle_exception(ex)

    def handle_message(self, msg_dict, queue):
        logging.info("handle_message.msg_dict="+str(msg_dict))
        handle_server = HandlerServer(self.mbd_flows, queue, self.mbd_flow_manager
                                      , self.zk_hosts, self.zk_root_path, self.zk_locker)
        handle_server.handle_msg(msg_dict)

    def setup_mbd_flow_manager(self):
        mongo_cfg = cm.config['mongo_mbd']
        mongo_client = mongo.Mongo(mongo_cfg['host'], mongo_cfg['user'], mongo_cfg['pw'], mongo_cfg['db'])
        mongo_collection = cm.config['mongo_mbd']['collection']
        self.mbd_flow_manager = mf.MBDFlowManager(mongo_client, mongo_collection, self.default_flow)
        if isinstance(self.mbd_flows, (list, tuple)):
            for f in self.mbd_flows:
                self.mbd_flow_manager.register_flow(f)
        else:
            self.mbd_flow_manager.register_flow(self.mbd_flows)
        logging.info("mbd flow manager setup finished")

    def setup_distributed_lock(self):
        self.zk_hosts = cm.config['zookeeper']['host']
        self.zk_root_path = cm.config['zookeeper']['root_path']
        self.zk_locker = dl.DistributedLock(self.zk_hosts, logger=logging.getLogger('elogger'))
        self.zk_locker.ensure_path(self.zk_root_path)
        logging.info("distributed lock setup finished")


class HandlerServer:
    def __init__(self, mbd_flows, queue, mbd_flow_manager,
                 zk_hosts, zk_root_path, zk_locker):
        super().__init__()
        self.queue = queue
        self.mbd_flows = mbd_flows
        self.mbd_flow_manager = mbd_flow_manager
        self.zk_hosts = zk_hosts
        self.zk_root_path = zk_root_path
        self.zk_locker = zk_locker

    def handle_msg(self, msg_dict):
        logging.info("start to handle msg=======")
        lock_success = False
        unlock_success = False
        app_id = None
        try:
            app_id = self.__get_key_message(msg_dict)
            lock_success = self.zk_locker.try_lock(self.__build_lock_path(app_id))
            logging.info("lock res = " + str(lock_success))
            if not lock_success:
                # if not lock successfully, send the message back to queue
                # sleep for a while, let other flow to finish the current same app_id
                time.sleep(0.1)
                self.queue.send_message(msg_dict)
            else:
                self.mbd_flow_manager.receive_message(app_id, msg_dict)
                unlock_success = self.zk_locker.try_unlock(self.__build_lock_path(app_id))
        except:
            logging.exception("handle msg error...")
            if lock_success and not unlock_success:
                self.zk_locker.try_unlock(self.__build_lock_path(app_id))
            raise

    def __build_lock_path(self, app_id):
        return "{0}/{1}".format(self.zk_root_path, app_id)

    @classmethod
    def __get_key_message(cls, message):
        if 'data' in message and 'appId' in message['data']:
            return message['data']['appId']
        if 'app_id' in message:
            return message['app_id']
        if 'appId' in message:
            return message['appId']
        return None
