from test.e2e.base import BaseScenariosTestCase


class ScenariosTestCase(BaseScenariosTestCase):
    scenario_name = 'four_players'

    def test_scenario(self):
        self.run_steps()
