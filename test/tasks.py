import unittest


class TestsTasks(object):
    def init_tasks(self, app):
        app.cli.command()(test)


def test():
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)
