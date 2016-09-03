import unittest
from flask_script import Command, Option

from utils.redis import redis


class TestsTasks(object):
    def init_tasks(self, manager):
        manager.add_command('test', Test())


class Test(Command):
    option_list = (
        Option('--file', '-f', dest='file', default='.'),
        Option('--test', '-t', dest='test'),
    )

    def run(self, test, file):
        loader = unittest.TestLoader()

        if test:
            tests = loader.loadTestsFromName(file + '.' + test)
        else:
            tests = loader.discover(file)

        testRunner = unittest.runner.TextTestRunner()

        redis.flushdb()
        testRunner.run(tests)
