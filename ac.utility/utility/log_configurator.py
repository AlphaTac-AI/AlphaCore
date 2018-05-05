import os
import logging.config
import yaml
import logging

__already_configured = False


def setup_logging(
        default_config_path='logging.yaml',
        default_level=logging.INFO,
        env_key='LOG_CFG',
        log_path='./log'):
    """
    Setup logging configuration
    """
    global __already_configured
    if __already_configured:
        return

    # if log path not exists, mkdir
    if log_path and (not os.path.isdir(log_path)):
        os.mkdir(log_path)

    # load log config file
    config_path = default_config_path
    value = os.getenv(env_key, None)
    if value:
        config_path = value
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    __already_configured = True
