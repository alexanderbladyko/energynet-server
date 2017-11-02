FAKE_MAP_CONFIG = {
    'colors': [
        '#bc3029',
        '#d8dd37',
        '#48d635',
        '#2c97c1',
        '#393a3a',
        '#c66ad8'
    ],
    'startCash': 50,
    'areas': [
        {'name': 'area1', 'color': '#70d06f'},
        {'name': 'area2', 'color': '#c9619d'},
        {'name': 'area3', 'color': '#e2dc3e'},
        {'name': 'area4', 'color': '#f11616'},
        {'name': 'area5', 'color': '#5e74b0'},
        {'name': 'area6', 'color': '#ec6c18'}
    ],
    'auction': {
        'removeOnFirstPass': False,
        'removeOnAnyonePass': False,
        'removeStationsLowNetworkSize': False,
    },
    'resourceLimits': {
        'uranium': 12, 'coal': 24, 'oil': 24, 'waste': 24
    },
    'resourceGroup': {
        'uranium': 1, 'coal': 3, 'oil': 3, 'waste': 3
    },
    'resourceInitials': {
        'uranium': 7, 'coal': 18, 'oil': 24, 'waste': 0
    },
    'initialStationRules': [
        {'cost': 10, 'place': 0, 'delta': 3},
        {'cost': 11, 'place': 0, 'delta': 4},
        {'cost': 13, 'place': 0},
        {'cost': 3, 'place': 0},
        {'cost': 4, 'place': 1},
        {'cost': 5, 'place': 2},
        {'cost': 7, 'place': 3},
        {'cost': 8, 'place': 4},
        {'cost': 9, 'place': 5},
        {'cost': -1, 'place': -1},
    ],
    'payment': [
        10, 22, 33, 44, 54, 64, 73, 82, 90, 98, 105, 112, 118, 124, 129, 134,
        138, 142, 145, 148, 150
    ],
    'junctions': [
        {'cost': 3, 'between': ['moscow', 'tula']},
        {'cost': 3, 'between': ['ryazan', 'moscow']},
        {'cost': 14, 'between': ['peterburg', 'arkhangelsk']},
        {'cost': 15, 'between': ['murmansk', 'arkhangelsk']},
        {'cost': 19, 'between': ['murmansk', 'peterburg']},
        {'cost': 15, 'between': ['kaliningrad', 'peterburg']},
        {'cost': 10, 'between': ['moscow', 'peterburg']},
        {'cost': 20, 'between': ['kaliningrad', 'tula']},
        {'cost': 0, 'between': ['tula', 'ryazan']},
        {'cost': 5, 'between': ['tula', 'voronezh']},
        {'cost': 5, 'between': ['voronezh', 'ryazan']},
        {'cost': 9, 'between': ['voronezh', 'rostov']},
        {'cost': 4, 'between': ['krasnodar', 'rostov']},
        {'cost': 14, 'between': ['krasnodar', 'mahachkala']},
        {'cost': 8, 'between': ['astrakhan', 'mahachkala']},
        {'cost': 9, 'between': ['krasnodar', 'volgograd']},
        {'cost': 11, 'between': ['volgograd', 'mahachkala']},
        {'cost': 6, 'between': ['volgograd', 'astrakhan']},
        {'cost': 7, 'between': ['rostov', 'volgograd']},
        {'cost': 6, 'between': ['saratov', 'volgograd']},
        {'cost': 8, 'between': ['voronezh', 'volgograd']},
        {'cost': 11, 'between': ['ulyanovsk', 'voronezh']},
        {'cost': 6, 'between': ['ulyanovsk', 'saratov']},
        {'cost': 8, 'between': ['saratov', 'voronezh']},
        {'cost': 5, 'between': ['samara', 'saratov']},
        {'cost': 7, 'between': ['nizhnekamsk', 'orenburg']},
        {'cost': 8, 'between': ['ufa', 'chelyabinsk']},
        {'cost': 13, 'between': ['omsk', 'chelyabinsk']},
        {'cost': 11, 'between': ['omsk', 'barnaul']},
        {'cost': 6, 'between': ['barnaul', 'novokuznetsk']},
        {'cost': 21, 'between': ['novokuznetsk', 'irkutsk']},
        {'cost': 6, 'between': ['irkutsk', 'ulan_ude']},
        {'cost': 6, 'between': ['ulan_ude', 'chita']},
        {'cost': 14, 'between': ['bratsk', 'ulan_ude']},
        {'cost': 29, 'between': ['norilsk', 'bratsk']},
        {'cost': 24, 'between': ['tomsk', 'norilsk']},
        {'cost': 3, 'between': ['tomsk', 'kemerovo']},
        {'cost': 7, 'between': ['kemerovo', 'krasnoyarsk']},
        {'cost': 10, 'between': ['krasnoyarsk', 'bratsk']},
        {'cost': 17, 'between': ['tomsk', 'bratsk']},
        {'cost': 4, 'between': ['novosibiirsk', 'kemerovo']},
        {'cost': 4, 'between': ['novosibirsk', 'tomsk']},
        {'cost': 4, 'between': ['novosibirsk', 'barnaul']},
        {'cost': 3, 'between': ['kemerovo', 'novokuznetsk']},
        {'cost': 5, 'between': ['novosibirsk', 'novokuznetsk']},
        {'cost': 7, 'between': ['novokuznetsk', 'krasnoyarsk']},
        {'cost': 17, 'between': ['krasnoyarsk', 'irkutsk']},
        {'cost': 10, 'between': ['omsk', 'novosibirsk']},
        {'cost': 12, 'between': ['omsk', 'tomsk']},
        {'cost': 15, 'between': ['surgut', 'tomsk']},
        {'cost': 19, 'between': ['surgut', 'norilsk']},
        {'cost': 10, 'between': ['surgut', 'tyumen']},
        {'cost': 19, 'between': ['tyumen', 'tomsk']},
        {'cost': 9, 'between': ['tyumen', 'omsk']},
        {'cost': 5, 'between': ['ekaterinburg', 'tyumen']},
        {'cost': 3, 'between': ['chelyabinsk', 'ekaterinburg']},
        {'cost': 5, 'between': ['tyumen', 'chelyabinsk']},
        {'cost': 21, 'between': ['syktyvkar', 'surgut']},
        {'cost': 17, 'between': ['syktyvkar', 'tyumen']},
        {'cost': 8, 'between': ['syktyvkar', 'perm']},
        {'cost': 5, 'between': ['ekaterinburg', 'perm']},
        {'cost': 6, 'between': ['ekaterinburg', 'ufa']},
        {'cost': 8, 'between': ['nizhnekamsk', 'ekaterinburg']},
        {'cost': 6, 'between': ['kirov', 'perm']},
        {'cost': 6, 'between': ['kirov', 'syktyvkar']},
        {'cost': 2, 'between': ['kazan', 'cheboksary']},
        {'cost': 3, 'between': ['nizhnekamsk', 'kazan']},
        {'cost': 5, 'between': ['kirov', 'cheboksary']},
        {'cost': 8, 'between': ['perm', 'kazan']},
        {'cost': 6, 'between': ['nizhnekamsk', 'perm']},
        {'cost': 4, 'between': ['cheboksary', 'ulyanovsk']},
        {'cost': 3, 'between': ['cheboksary', 'novgorod']},
        {'cost': 3, 'between': ['ulyanovsk', 'ryazan']},
        {'cost': 7, 'between': ['moscow', 'novgorod']},
        {'cost': 3, 'between': ['moscow', 'yaroslavl']},
        {'cost': 4, 'between': ['novgorod', 'yaroslavl']},
        {'cost': 10, 'between': ['syktyvkar', 'arkhangelsk']},
        {'cost': 12, 'between': ['yaroslavl', 'arkhangelsk']},
        {'cost': 11, 'between': ['syktyvkar', 'novgorod']},
        {'cost': 9, 'between': ['peterburg', 'yaroslavl']},
        {'cost': 3, 'between': ['samara', 'ulyanovsk']},
        {'cost': 4, 'between': ['kazan', 'samara']},
        {'cost': 13, 'between': ['tula', 'peterburg']},
        {'cost': 3, 'between': ['ulyanovsk', 'kazan']},
        {'cost': 6, 'between': ['samara', 'orenburg']},
        {'cost': 6, 'between': ['ufa', 'orenburg']},
        {'cost': 4, 'between': ['nizhnekamsk', 'ufa']},
        {'cost': 5, 'between': ['samara', 'nizhnekamsk']},
        {'cost': 10, 'between': ['bratsk', 'irkutsk']}
    ],
    'cities': [
        {'area': 'area1', 'name': 'murmansk', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'peterburg', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'kaliningrad', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'moscow', 'slots': [10, 15, 20]},
        {'area': 'area3', 'name': 'voronezh', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'tula', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'ryazan', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'arkhangelsk', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'novgorod', 'slots': [10, 15, 20]},
        {'area': 'area4', 'name': 'samara', 'slots': [10, 15, 20]},
        {'area': 'area3', 'name': 'saratov', 'slots': [10, 15, 20]},
        {'area': 'area3', 'name': 'astrakhan', 'slots': [10, 15, 20]},
        {'area': 'area3', 'name': 'mahachkala', 'slots': [10, 15, 20]},
        {'area': 'area3', 'name': 'krasnodar', 'slots': [10, 15, 20]},
        {'area': 'area3', 'name': 'volgograd', 'slots': [10, 15, 20]},
        {'area': 'area4', 'name': 'ufa', 'slots': [10, 15, 20]},
        {'area': 'area4', 'name': 'chelyabinsk', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'omsk', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'barnaul', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'novosibirsk', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'kemerovo', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'krasnoyarsk', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'tomsk', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'surgut', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'bratsk', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'chita', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'ulan_ude', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'irkutsk', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'norilsk', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'kazan', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'nizhnekamsk', 'slots': [10, 15, 20]},
        {'area': 'area4', 'name': 'perm', 'slots': [10, 15, 20]},
        {'area': 'area2', 'name': 'yaroslavl', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'kirov', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'syktyvkar', 'slots': [10, 15, 20]},
        {'area': 'area5', 'name': 'tyumen', 'slots': [10, 15, 20]},
        {'area': 'area4', 'name': 'ekaterinbur', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'ulyanovsk', 'slots': [10, 15]},
        {'area': 'area3', 'name': 'rostov', 'slots': [10, 15, 20]},
        {'area': 'area6', 'name': 'novokuznets', 'slots': [10, 15, 20]},
        {'area': 'area1', 'name': 'cheboksary', 'slots': [10, 15, 20]},
        {'area': 'area4', 'name': 'orenburg', 'slots': [10, 15, 20]}
    ],
    'userStationsCount': [4, 3, 3, 3, 3],
    'secondPhaseCitiesCount': [10, 7, 7, 7, 6],
    'endGameCitiesCount': [21, 17, 17, 15, 14],
    'stations': [
        {
            'cost': 3.0,
            'capacity': 2,
            'efficiency': 1,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 4.0,
            'capacity': 2,
            'efficiency': 1,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 5.0,
            'capacity': 2,
            'efficiency': 1,
            'resources': [
                'coal',
                'oil'
            ]
        },
        {
            'cost': 7.0,
            'capacity': 3,
            'efficiency': 2,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 8.0,
            'capacity': 3,
            'efficiency': 2,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 9.0,
            'capacity': 1,
            'efficiency': 1,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 10.0,
            'capacity': 2,
            'efficiency': 2,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 11.0,
            'capacity': 1,
            'efficiency': 2,
            'resources': [
                'uranium'
            ]
        },
        {
            'cost': 12.0,
            'capacity': 2,
            'efficiency': 2,
            'resources': [
                'coal',
                'oil'
            ]
        },
        {
            'cost': 13.0,
            'capacity': 0,
            'efficiency': 1,
            'resources': []
        },
        {
            'cost': 15.0,
            'capacity': 2,
            'efficiency': 3,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 16.0,
            'capacity': 2,
            'efficiency': 3,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 17.0,
            'capacity': 1,
            'efficiency': 2,
            'resources': [
                'uranium'
            ]
        },
        {
            'cost': 18.0,
            'capacity': 0,
            'efficiency': 2,
            'resources': []
        },
        {
            'cost': 19.0,
            'capacity': 2,
            'efficiency': 3,
            'resources': [
                'waste'
            ]
        },
        {
            'cost': 20.0,
            'capacity': 3,
            'efficiency': 5,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 21.0,
            'capacity': 2,
            'efficiency': 4,
            'resources': [
                'coal',
                'oil'
            ]
        },
        {
            'cost': 22.0,
            'capacity': 0,
            'efficiency': 2,
            'resources': []
        },
        {
            'cost': 23.0,
            'capacity': 1,
            'efficiency': 3,
            'resources': [
                'uranium'
            ]
        },
        {
            'cost': 24.0,
            'capacity': 2,
            'efficiency': 4,
            'resources': [
                'waste'
            ]
        },
        {
            'cost': 25.0,
            'capacity': 2,
            'efficiency': 5,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 26.0,
            'capacity': 2,
            'efficiency': 5,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 27.0,
            'capacity': 0,
            'efficiency': 3,
            'resources': []
        },
        {
            'cost': 28.0,
            'capacity': 1,
            'efficiency': 4,
            'resources': [
                'uranium'
            ]
        },
        {
            'cost': 29.0,
            'capacity': 1,
            'efficiency': 4,
            'resources': [
                'coal',
                'oil'
            ]
        },
        {
            'cost': 30.0,
            'capacity': 3,
            'efficiency': 6,
            'resources': [
                'waste'
            ]
        },
        {
            'cost': 31.0,
            'capacity': 3,
            'efficiency': 6,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 32.0,
            'capacity': 3,
            'efficiency': 6,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 33.0,
            'capacity': 0,
            'efficiency': 4,
            'resources': []
        },
        {
            'cost': 33.5,
            'capacity': 3,
            'efficiency': 6,
            'resources': [
                'coal',
                'oil',
                'waste',
                'uranium'
            ]
        },
        {
            'cost': 34.0,
            'capacity': 1,
            'efficiency': 5,
            'resources': [
                'uranium'
            ]
        },
        {
            'cost': 35.0,
            'capacity': 1,
            'efficiency': 5,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 36.0,
            'capacity': 3,
            'efficiency': 7,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 37.0,
            'capacity': 0,
            'efficiency': 4,
            'resources': []
        },
        {
            'cost': 38.0,
            'capacity': 3,
            'efficiency': 7,
            'resources': [
                'waste'
            ]
        },
        {
            'cost': 39.0,
            'capacity': 1,
            'efficiency': 6,
            'resources': [
                'uranium'
            ]
        },
        {
            'cost': 40.0,
            'capacity': 2,
            'efficiency': 6,
            'resources': [
                'oil'
            ]
        },
        {
            'cost': 42.0,
            'capacity': 2,
            'efficiency': 6,
            'resources': [
                'coal'
            ]
        },
        {
            'cost': 44.0,
            'capacity': 0,
            'efficiency': 5,
            'resources': []
        },
        {
            'cost': 46.0,
            'capacity': 3,
            'efficiency': 7,
            'resources': [
                'coal',
                'oil'
            ]
        },
        {
            'cost': 50.0,
            'capacity': 0,
            'efficiency': 6,
            'resources': []
        },
        {
            'cost': -1,
            'capacity': 0,
            'efficiency': 0,
            'resources': []
        }
    ],
    'activeStationsCount': 3,
    'visibleStationsCount': 6,
    'areasCount': [3, 3, 4, 5, 5],
    'refill': [
        {
            'uranium': [0, 1, 1, 1, 2, 2],
            'coal': [0, 2, 2, 3, 4, 5],
            'oil': [0, 3, 3, 5, 5, 7],
            'waste': [0, 2, 2, 3, 4, 4]
        },
        {
            'uranium': [0, 1, 1, 1, 2, 2],
            'coal': [0, 2, 3, 4, 5, 6],
            'oil': [0, 4, 4, 6, 7, 9],
            'waste': [0, 2, 2, 3, 3, 5]
        },
        {
            'uranium': [0, 1, 1, 2, 2, 3],
            'coal': [0, 4, 4, 5, 6, 7],
            'oil': [0, 3, 3, 4, 5, 6],
            'waste': [0, 3, 3, 4, 5, 6]
        },
    ]
}
