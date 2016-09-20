from flask_script import Command
from yoyo import read_migrations, get_backend

from utils.config import config


class DbTasks(object):
    def init_tasks(self, manager):
        manager.add_command('sync_db', SyncDb())


class SyncDb(Command):
    def run(self):
        backend = get_backend(config.get('db', 'url'))
        migrations = read_migrations(config.get('db', 'migrations'))
        backend.apply_migrations(backend.to_apply(migrations))
        print('Done')
