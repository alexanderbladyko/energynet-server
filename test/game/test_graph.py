from test.base import BaseTest

from game.graph import get_closest_paths


class TestGraphClosestPathTestCase(BaseTest):
    def test_triangle(self):
        map_config = {
            'junctions': [
                {
                    'between': ['A', 'B'],
                    'cost': 2,
                },
                {
                    'between': ['A', 'C'],
                    'cost': 4,
                },
                {
                    'between': ['B', 'C'],
                    'cost': 3,
                },
            ],
        }
        result = get_closest_paths(map_config, ['A'], ['C'])
        self.assertEqual(result, {
            'C': 4,
        })

    def test_multiple_vertices(self):
        map_config = {
            'junctions': [
                {
                    'between': ['A', 'B'],
                    'cost': 2,
                },
                {
                    'between': ['B', 'C'],
                    'cost': 3,
                },
                {
                    'between': ['D', 'C'],
                    'cost': 6,
                },
            ],
        }
        result = get_closest_paths(map_config, ['A', 'C'], ['B', 'D'])
        self.assertEqual(result, {
            'B': 2,
            'D': 6,
        })

    def test_single_vertex(self):
        map_config = {
            'junctions': [
                {
                    'between': ['A', 'B'],
                    'cost': 2,
                },
                {
                    'between': ['A', 'C'],
                    'cost': 4,
                },
                {
                    'between': ['B', 'C'],
                    'cost': 3,
                },
                {
                    'between': ['D', 'C'],
                    'cost': 5,
                },
            ],
        }
        result = get_closest_paths(map_config, ['A'], ['D'])
        self.assertEqual(result, {
            'D': 9,
        })

    def test_complex(self):
        map_config = {
            'junctions': [
                {
                    'between': ['A', 'B'],
                    'cost': 3,
                },
                {
                    'between': ['A', 'C'],
                    'cost': 10,
                },
                {
                    'between': ['A', 'D'],
                    'cost': 5,
                },
                {
                    'between': ['B', 'C'],
                    'cost': 8,
                },
                {
                    'between': ['B', 'F'],
                    'cost': 7,
                },
                {
                    'between': ['C', 'E'],
                    'cost': 12,
                },
                {
                    'between': ['C', 'F'],
                    'cost': 10,
                },
                {
                    'between': ['C', 'G'],
                    'cost': 13,
                },
                {
                    'between': ['D', 'G'],
                    'cost': 6,
                },
                {
                    'between': ['E', 'F'],
                    'cost': 8,
                },
                {
                    'between': ['E', 'G'],
                    'cost': 7,
                },
            ],
        }
        result = get_closest_paths(map_config, ['A', 'D'], ['C', 'F'])
        self.assertEqual(result, {
            'C': 10,
            'F': 10,
        })
        result = get_closest_paths(map_config, ['A', 'D'], ['B', 'F'])
        self.assertEqual(result, {
            'B': 3,
            'F': 7,
        })
        result = get_closest_paths(map_config, ['B', 'C'], ['G', 'D'])
        self.assertEqual(result, {
            'G': 6,
            'D': 8,
        })
