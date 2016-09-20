from flask_script import Manager

from db.tasks import DbTasks
from test.tasks import TestsTasks

from utils.server import app


manager = Manager(app)


tasks = [
    DbTasks(),
    TestsTasks(),
]

for instance in tasks:
    instance.init_tasks(manager)


if __name__ == "__main__":
    manager.run()
