from flask_script import Manager

from config.tasks import ConfigTasks
from db.tasks import DbTasks
from test.tasks import TestsTasks




manager = Manager(app)


tasks = [
    DbTasks(),
    TestsTasks(),
    ConfigTasks(),
]

for instance in tasks:
    instance.init_tasks(manager)


if __name__ == "__main__":
    manager.run()
