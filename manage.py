from flask_script import Manager

from config.tasks import ConfigTasks
from db.tasks import DbTasks

from app import app


manager = Manager(app)


tasks = [
    DbTasks(),
    ConfigTasks(),
]

for instance in tasks:
    instance.init_tasks(manager)


if __name__ == "__main__":
    manager.run()
