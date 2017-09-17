from unittest.mock import patch
from test.base import BaseTest

from game.logic import get_start_stations


class GetStartStationsTestCase(BaseTest):
    def setUp(self):

        self.stations_config = [
            {'cost': 5, 'capacity': 2, 'efficiency': 1},
            {'cost': 4, 'capacity': 2, 'efficiency': 1},
            {'cost': 8, 'capacity': 3, 'efficiency': 2},
            {'cost': 7, 'capacity': 3, 'efficiency': 2},
            {'cost': 3, 'capacity': 2, 'efficiency': 1},
            {'cost': 9, 'capacity': 1, 'efficiency': 1},
            {'cost': 10, 'capacity': 2, 'efficiency': 2},
            {'cost': 11, 'capacity': 1, 'efficiency': 2},
            {'cost': 12, 'capacity': 2, 'efficiency': 2},
            {'cost': 13, 'capacity': 0, 'efficiency': 1},
            {'cost': 15, 'capacity': 2, 'efficiency': 3},
            {'cost': 16, 'capacity': 2, 'efficiency': 3},
            {'cost': 17, 'capacity': 1, 'efficiency': 2},
            {'cost': 18, 'capacity': 0, 'efficiency': 2},
            {'cost': 19, 'capacity': 2, 'efficiency': 3},
            {'cost': 20, 'capacity': 3, 'efficiency': 5},
            {'cost': 21, 'capacity': 2, 'efficiency': 4},
            {'cost': -1, 'capacity': 0, 'efficiency': 2},
            {'cost': 22, 'capacity': 0, 'efficiency': 2},
        ]
        self.stations = [s['cost'] for s in self.stations_config]

        super().setUp()

    def test_config(self):
        fake_map_config = self.test_map_config.copy()
        fake_map_config['stations'] = self.stations_config
        with patch('random.shuffle', return_value=self.stations):
            with patch('random.randint', return_value=2):
                result = get_start_stations(fake_map_config)

        self.assertEqual(result, [
            3, 4, 5, 7, 8, 9, 13, 12, 15, 11, 10,
            16, 17, 18, 19, 20, 21, 22, -1
        ])
