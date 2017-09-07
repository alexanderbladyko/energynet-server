import sys
import heapq


def get_graph(junctions):
    graph = {}
    for junction in junctions:
        from_city, to_city = junction['between']
        graph[from_city] = {}
        graph[to_city] = {}
    for junction in junctions:
        from_city, to_city = junction['between']
        graph[from_city][to_city] = junction['cost']
        graph[to_city][from_city] = junction['cost']
    return graph


def get_closest_paths(map_config, from_cities, to_cities):
    graph = get_graph(map_config.get('junctions'))

    distances = {}
    nodes = []
    result = {}

    for city in graph.keys():
        if city in from_cities:
            distances[city] = 0
            heapq.heappush(nodes, [0, city])
        else:
            distances[city] = sys.maxsize
            heapq.heappush(nodes, [sys.maxsize, city])

    while nodes:
        distance, city = heapq.heappop(nodes)
        if distance == sys.maxsize:
            break

        if city in to_cities:
            if city in result and result[city] < distance:
                break
            result[city] = distance
            distances[city] = 0

        neighbors = graph[city]
        for neighbor, cost in neighbors.items():
            alt = distances[city] + cost

            if alt < distances[neighbor]:
                distances[neighbor] = alt
                heapq.heappush(nodes, [alt, neighbor])
                heapq.heapify(nodes)

    return result
