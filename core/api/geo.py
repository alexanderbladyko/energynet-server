import os
from flask import send_from_directory


def geo_data(map_name):
    current_dir = os.getcwd()
    folder = 'config/data/{map_name}/generated'.format(map_name=map_name)
    root = os.path.join(current_dir, folder)
    return send_from_directory(root, 'geo.json')
