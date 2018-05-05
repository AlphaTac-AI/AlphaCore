import logging
import os
import yaml
import json


config = None
config_db_table = "ml_configs"


def setup_config(default_config_path='config.yaml'):
    global config
    if config:
        return

    # load config file
    config_path = default_config_path
    if not os.path.exists(config_path):
        logging.warning("Config file not found. file path: %s", config_path)
        return

    with open(config_path, 'rt') as f:
        config = yaml.safe_load(f.read())

    # load config from database
    if config.get('db_config'):
        __setup_config_from_db()


def setup_config_multi(config_path='config.yaml'):
    '''load multiple configure file

    if there are some same configure in many files, then
    the last configure will replace the configure before there.
    this must be careful.
    >>> len(setup_config_multi('config.yaml'))
    1
    >>> len(setup_config_multi('logging.yaml'))
    7
    '''
    global config

    if not os.path.exists(config_path):
        logging.error("Config file is not found. File path: {config_path}".format(config_path=config_path))
        return None

    if not config:
        config = {}

    with open(config_path, 'rt') as f:
        config = dict(config, **yaml.safe_load(f.read()))

    # load config from database
    if config.get('db_config'):
        __setup_config_from_db()

    # for doctest
    return config


def set_config_db_table(table_name):
    global config_db_table
    config_db_table = table_name


# def __setup_config_from_db():
#     client = mysql.MySql(**config['db_config']['database'])
#     service = config['db_config']['service']
#
#     sql = "select cfg_key, cfg_value, value_type from {} where service = '{}'".format(config_db_table, service)
#     db_cfgs = client.query(sql)
#     for cfg in db_cfgs:
#         vtype = cfg['value_type']
#         if vtype == 'int':
#             config[cfg['cfg_key']] = int(cfg['cfg_value'])
#         elif vtype == 'float':
#             config[cfg['cfg_key']] = float(cfg['cfg_value'])
#         elif vtype == 'bool':
#             config[cfg['cfg_key']] = (cfg['cfg_value'].upper() in ['TRUE', '1'])
#         elif vtype == 'str':
#             config[cfg['cfg_key']] = cfg['cfg_value']
#         elif vtype == 'json':
#             config[cfg['cfg_key']] = json.loads(cfg['cfg_value'])
