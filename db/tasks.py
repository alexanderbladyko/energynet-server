from yoyo import read_migrations, get_backend

from utils.config import config


class DbTasks(object):
    def init_tasks(self, app):
        app.cli.command()(sync_db)


def sync_db():
    backend = get_backend(config.get('db', 'url'))
    migrations = read_migrations(config.get('db', 'migrations'))
    backend.apply_migrations(backend.to_apply(migrations))
    print('Done')
