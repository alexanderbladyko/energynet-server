from db.tasks import DbTasks
from test.tasks import TestsTasks

from utils.server import app

tasks = [
    DbTasks(),
    TestsTasks(),
]


def init_tasks():
    for instance in tasks:
        instance.init_tasks(app)
