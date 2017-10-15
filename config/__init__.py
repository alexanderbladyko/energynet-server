import os

from yaml import load


class ConfigData:
    def __init__(self):
        current_dir = os.getcwd()
        root = os.path.join(current_dir, 'config/data')

        self.maps = {}
        for map_name in os.listdir(root):
            if os.path.isdir(os.path.join(root, map_name)):
                folder = os.path.join(root, map_name)

                data = {}
                data.update(load(open(folder+'/common.yaml', 'r')))
                data.update(load(open(folder+'/map.yaml', 'r')))
                data.update(load(open(folder+'/stations.yaml', 'r')))
                data.update(load(open(folder+'/steps.yaml', 'r')))
                self.maps[map_name] = data


config = ConfigData()
