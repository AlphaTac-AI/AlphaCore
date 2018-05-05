import logging
import os
import yaml

__config_in_memory = {}
__config_file = None


def setup(config_path='dynamic_config.yaml'):
    """
    this method MUST be called FIRST before any of other methods in this module when being imported
    """
    global __config_file
    if __config_file:
        return
    # load config file
    if not os.path.exists(config_path):
        logging.warn("Config file not found. file path: %s", config_path)
        return
    __config_file = config_path


def get(key):
    """
    get config according to priority
    1. file config
    2. config set by 'put' method, in memory
    """
    fc = __file_config()
    global __config_in_memory
    if key in fc and fc[key]:
        return fc[key]
    if key in __config_in_memory:
        return __config_in_memory[key]
    return None


def put(key, value):
    global __config_in_memory
    __config_in_memory[key] = value


def __file_config():
    global __config_file
    with open(__config_file, 'rt') as f:
        return yaml.safe_load(f.read())
