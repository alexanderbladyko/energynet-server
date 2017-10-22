import re
from flask_script import Command
from subprocess import call
from yoyo import read_migrations, get_backend
from utils.config import config


class DbTasks(object):
    def init_tasks(self, manager):
        manager.add_command('sync_db', SyncDb())
        manager.add_command('db_shell', DbShell())


class SyncDb(Command):
    def run(self):
        backend = get_backend(config.get('db', 'url'))
        migrations = read_migrations(config.get('db', 'migrations'))
        backend.apply_migrations(backend.to_apply(migrations))
        print('Done')


REGEX = 'postgresql://(.*?):(.*?)@(.*?)/(.*)'


class DbShell(Command):
    def run(self):
        db_url = config.get('db', 'url')
        user, password, host, database = re.search(REGEX, db_url).groups()
        call([
            'psql',
            '-h', host,
            '-U', user,
            '-d', database
        ], env={'PGPASSWORD': password})
