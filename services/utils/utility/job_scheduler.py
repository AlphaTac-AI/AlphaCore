from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from mlx_server import server
from mlx_database import mongo
from mlx_utility import config_manager as cm
import tzlocal
import logging


class JobScheduler(server.Server):
    def __init__(self):
        super(JobScheduler, self).__init__()
        self.mongo_client = None
        self.scheduler = None
        self.setup_mongo()
        self.setup_scheduler()

    def add_job(self, func, trigger=None, args=None, kwargs=None, id=None, name=None, **trigger_args):
        """
        'trigger': refer to apscheduler.triggers
        """
        self.scheduler.add_job(func, trigger=trigger, args=args, kwargs=kwargs, id=id, name=name, jobstore='mongo',
                               executor='default', replace_existing=True, **trigger_args)
        logging.info(
            "job added. func: {}, trigger: {}, args: {}, kwargs: {}, id: {}, name: {}, trigger_args: {}".format(
                func.__name__, trigger, args, kwargs, id, name, trigger_args))
        return self

    def run(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        logging.info("job scheduler is stopped.")

    def setup_mongo(self):
        mc = cm.config['mongo_scheduler']  # config named 'mongo_scheduler' is a must, or to override this method
        m = mongo.Mongo(**mc)
        self.mongo_client = m.get_conn()
        logging.info("mongo client setup done.")

    def setup_scheduler(self):
        mc = cm.config['mongo_scheduler']
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
            'mongo': MongoDBJobStore(client=self.mongo_client, database=mc['db'], collection=mc['collection'])
        }
        executors = {
            'default': ThreadPoolExecutor(10),
            'processpool': ProcessPoolExecutor(5)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        self.scheduler = BlockingScheduler(jobstores=jobstores,
                                           executors=executors,
                                           job_defaults=job_defaults,
                                           timezone=tzlocal.get_localzone())
        self.scheduler.add_listener(self.__listener)
        logging.info("scheduler setup done.")

    @staticmethod
    def __listener(event):
        logging.info('received scheduler event: %s', event)
