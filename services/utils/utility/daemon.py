import sys
import os
from signal import signal
import getopt
from utility import log_configurator as lc, config_manager as cm
import logging


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    SIG_STOP = 10

    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        pid_dir = '/tmp/AlphaCore'
        if not os.path.isdir(pid_dir):
            os.mkdir(pid_dir)
        self.pidfile = "{0}/{1}.pid".format(pid_dir, self.__class__.__name__)
        self.working_dir = os.getcwd()
        self.server = None

    def setup_server(self):
        raise NotImplementedError("server must be set to run!")

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        print("daemonize started ...")
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            print("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            print("fork #2 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

        # write pidfile
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid)

        os.chdir(self.working_dir)
        print("daemonize finished")

    def delpid(self):
        os.remove(self.pidfile)
        print("PID file removed. file: {}".format(self.pidfile))

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            print("pidfile {} already exist. Daemon already running?".format(self.pidfile))
            sys.exit(1)

        # Start the daemon, run the server
        self.setup_log()
        self.setup_config()
        self.daemonize()
        self.setup_server()  # only set server before run
        self.setup_signal_handler()
        self.server.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            print("pidfile {} does not exist. Daemon not running?".format(self.pidfile))
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            os.kill(pid, self.SIG_STOP)
            self.delpid()
        except:
            print("try killing process or remove PID file failed!")
            print("Unexpected error: {}".format(sys.exc_info()[0]))
            sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def setup_log(self):
        lc.setup_logging()
        print("log setup finished")

    def setup_config(self):
        cm.setup_config()
        print("config setup finished")

    def setup_signal_handler(self):
        signal(self.SIG_STOP, self.signal_handler)

    def signal_handler(self, signum, frame):
        logging.info("signal received: {}".format(signum))
        if signum == self.SIG_STOP:
            logging.info("termination process is started. pls wait ...")
            self.server.stop()

    def main(self):
        """
        all server based classes should start/stop/restart with method 'main()'
        """
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
        except getopt.error as e:
            print(e)
            print('for help use --help')
            print("usage: {} start|stop|restart".format(sys.argv[0]))
            sys.exit(2)

        if len(args) == 1:
            if 'start' == args[0]:
                self.start()
            elif 'stop' == args[0]:
                self.stop()
            elif 'restart' == args[0]:
                self.restart()
            else:
                print("unknown command: {}".format(args[0]))
                sys.exit(2)
            sys.exit(0)
