import os
from configparser import SafeConfigParser


config_file_path = 'config_local.ini'
if os.getenv('TEST') in ['True', 'true', '1']:
    config_file_path = 'config_tests.ini'


config = SafeConfigParser()
config.read(config_file_path)
