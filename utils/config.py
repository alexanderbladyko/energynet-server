import os
from configparser import SafeConfigParser


config_file_path = os.getenv('ENERGYNET_CONFIG', 'config.ini')

config = SafeConfigParser()
config.read(config_file_path)
