FAKE_MAP_CONFIG = {
    'startCash': 33,
    'areas': [
        {'name': 'area1', 'color': '#70d06f'},
        {'name': 'area2', 'color': '#c9619d'},
        {'name': 'area3', 'color': '#e2dc3e'},
        {'name': 'area4', 'color': '#f11616'},
        {'name': 'area5', 'color': '#5e74b0'},
        {'name': 'area6', 'color': '#ec6c18'}
    ],
    'resourceLimits': {
        'uranium': 12, 'coal': 24, 'oil': 24, 'waste': 24
    },
    'resourceGroup': {
        'uranium': 1, 'coal': 3, 'oil': 3, 'waste': 3
    },
    'payment': [
        10, 22, 33, 44, 54, 64, 73, 82, 90, 98, 105, 112, 118, 124, 129, 134,
        138, 142, 145, 148, 150
    ],
    'junctions': [
        {'between': ['moscow', 'tula'], 'cost': 3},
        {'between': ['ryazan', 'moscow'], 'cost': 3},
        {'between': ['peterburg', 'arkhangelsk'], 'cost': 14},
        {'between': ['murmansk', 'arkhangelsk'], 'cost': 15},
        {'between': ['murmansk', 'peterburg'], 'cost': 19},
        {'between': ['kaliningrad', 'peterburg'], 'cost': 15},
        {'between': ['moscow', 'peterburg'], 'cost': 10},
        {'between': ['kaliningrad', 'tula'], 'cost': 20},
        {'between': ['tula', 'ryazan'], 'cost': 0},
        {'between': ['tula', 'voronezh'], 'cost': 5},
        {'between': ['voronezh', 'ryazan'], 'cost': 5},
        {'between': ['voronezh', 'rostov'], 'cost': 9},
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
    ],
    'userStationsCount': [4, 3, 3, 3, 3],
    'secondPhaseCitiesCount': [10, 7, 7, 7, 6],
    'endGameCitiesCount': [21, 17, 17, 15, 14],
    'stations': [
        {'resources': ['oil'], 'cost': 3, 'capacity': 2, 'efficiency': 1},
        {'resources': ['coal'], 'cost': 4, 'capacity': 2, 'efficiency': 1},
        {'resources': ['coal', 'oil'], 'cost': 5, 'capacity': 2, 'efficiency': 1},
        {'resources': ['oil'], 'cost': 7, 'capacity': 3, 'efficiency': 2},
        {'resources': ['coal'], 'cost': 8, 'capacity': 3, 'efficiency': 2},
        {'resources': ['oil'], 'cost': 9, 'capacity': 1, 'efficiency': 1},
        {'resources': ['coal'], 'cost': 10, 'capacity': 2, 'efficiency': 2},
        {'resources': ['uranium'], 'cost': 11, 'capacity': 1, 'efficiency': 2},
        {'resources': ['coal', 'oil'], 'cost': 12, 'capacity': 2, 'efficiency': 2},
        {'resources': [], 'cost': 13, 'capacity': 0, 'efficiency': 1},
        {'resources': ['coal'], 'cost': 15, 'capacity': 2, 'efficiency': 3},
        {'resources': ['oil'], 'cost': 16, 'capacity': 2, 'efficiency': 3},
        {'resources': ['uranium'], 'cost': 17, 'capacity': 1, 'efficiency': 2},
        {'resources': [], 'cost': 18, 'capacity': 0, 'efficiency': 2},
        {'resources': ['waste'], 'cost': 19, 'capacity': 2, 'efficiency': 3},
        {'resources': ['coal'], 'cost': 20, 'capacity': 3, 'efficiency': 5},
        {'resources': ['coal', 'oil'], 'cost': 21, 'capacity': 2, 'efficiency': 4},
        {'resources': [], 'cost': 22, 'capacity': 0, 'efficiency': 2},
    ],
    'areasCount': [3, 3, 4, 5, 5],
    'refill': [
        {'uranium': [0, 1, 1, 1, 2, 2], 'coal': [0, 2, 2, 3, 4, 5], 'oil': [0, 3, 3, 5, 5, 7], 'waste': [0, 2, 2, 3, 4, 4]},
        {'uranium': [0, 1, 1, 1, 2, 2], 'coal': [0, 2, 3, 4, 5, 6], 'oil': [0, 4, 4, 6, 7, 9], 'waste': [0, 2, 2, 3, 3, 5]},
        {'uranium': [0, 1, 1, 2, 2, 3], 'coal': [0, 4, 4, 5, 6, 7], 'oil': [0, 3, 3, 4, 5, 6], 'waste': [0, 3, 3, 4, 5, 6]}
    ]
}
