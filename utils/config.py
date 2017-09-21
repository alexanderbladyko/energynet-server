import os
from configparser import SafeConfigParser


if os.getenv('TEST') in ['True', 'true', '1']:
    config_file_path = 'config_tests.ini'
else:
    config_file_path = 'config_local.ini'


config = SafeConfigParser()
config.read(config_file_path)
