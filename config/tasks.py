import os
import json
import math
from flask_script import Command, Option
from psycopg2.extras import DictCursor
from yaml import load

from db.utils import get_db


class ConfigTasks:
    def init_tasks(self, manager):
        manager.add_command('config.load', Load())
        manager.add_command('config.delete', Delete())
        manager.add_command('config.normalize', Normalize())
        manager.add_command('config.geo.split', Split())
        manager.add_command('config.build', Build())
        manager.add_command('config.generate.map_data', GenerateMapData())


class Load(Command):
    option_list = (
        Option('--name', '-n', dest='name'),
        Option('--path', '-p', dest='path'),
    )

    def run(self, name, path, db=None):
        current_dir = os.getcwd()
        folder = ''
        if name:
            folder = os.path.join(current_dir, 'config/data/{0}'.format(name))
        if path:
            folder = os.path.join(current_dir, path)

        field_name = os.path.basename(os.path.normpath(folder))

        common_data = load(open(folder+'/common.yaml', 'r'))
        map_data = load(open(folder+'/map.yaml', 'r'))
        stations_data = load(open(folder+'/stations.yaml', 'r'))
        steps_data = load(open(folder+'/steps.yaml', 'r'))

        if db is None:
            db = get_db()

        with db.cursor(cursor_factory=DictCursor) as cursor:
            self._load_fields(cursor, field_name, common_data, steps_data)
            self._load_areas(cursor, field_name, map_data)
            self._load_cities(cursor, map_data)
            self._load_junctions(cursor, map_data)
            self._load_stations(cursor, field_name, stations_data)

            db.commit()

        # app.logger.info('Finished loading')

    def _load_fields(self, cursor, field_name, common_data, steps_data):
        data = common_data.copy()
        data.update({
            'steps': steps_data
        })
        cursor.execute(
            'insert into public.fields(name, data) values (%s, %s)',
            (field_name, json.dumps(data))
        )

    def _load_areas(self, cursor, field_name, map_data):
        for area in map_data['areas']:
            cursor.execute(
                'insert into public.areas(name, color, field_name) \
                values (%s, %s, %s)',
                (area['name'], area['color'], field_name)
            )

    def _load_cities(self, cursor, map_data):
        for city in map_data['cities']:
            cursor.execute(
                'insert into public.cities(name, area_name, slots) \
                values (%s, %s, %s)',
                (city['name'], city['area'], city['slots'])
            )

    def _load_junctions(self, cursor, map_data):
        for junction in map_data['junctions']:
            city_1, city_2 = junction['between']
            cursor.execute(
                'insert into public.junсtions(city_1, city_2, cost) \
                values (%s, %s, %s)',
                (city_1, city_2, junction['cost'])
            )

    def _load_stations(self, cursor, field_name, stations_data):
        for station in stations_data['stations']:
            cursor.execute(
                'insert into public.stations( \
                    cost, capacity, resources, field_name \
                ) values (%s, %s, %s, %s)',
                (station['cost'], station['capacity'], station['resources'],
                    field_name)
            )


class Delete(Command):
    option_list = (
        Option('--name', '-n', dest='name'),
    )

    def run(self, name, db=None):
        if db is None:
            db = get_db()

        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                'delete from public.stations where field_name=%s', (name,)
            )

            cursor.execute("""
delete from public.junсtions
where [junctions.city_1, junctions.city_2] && (
    select cities.name from cities
    join public.areas on areas.name = cities.area_name
    join public.fields on fields.name = areas.field_name
    where fields.name = %s
)
            """, (name, ))

            cursor.execute("""
delete from public.cities
where cities.area_name in (
    select areas.name from areas
    join public.fields ON fields.name = areas.field_name
    where fields.name = %s
)
            """, (name, ))

            cursor.execute(
                'delete from public.areas where field_name=%s', (name,)
            )

            cursor.execute('delete from public.fields where name=%s', (name,))

            db.commit()

        # app.logger.info('Finished deleting')


class Normalize(Command):
    option_list = (
        Option('--source', '-s', dest='source'),
        Option('--output', '-o', dest='output'),
        Option('--tolerance', '-t', dest='tolerance')
    )

    def run(self, source, output, tolerance=1, db=None):
        with open(source) as data_file:
            data = json.loads(data_file.read())

        self.points = []
        self.tolerance = float(tolerance)

        features = data['features']

        new_features = {
            'points': [],
            'lines': [],
            'polygons': [],
        }

        for feature in features:
            type = feature['geometry']['type']
            geo = feature['geometry']['coordinates']
            props = feature['properties']
            if type == 'Point':
                new_features['points'].append(
                    (type, self._find(geo), props)
                )
            elif type == 'LineString':
                new_features['lines'].append(
                    (type, self._find_line_points(geo), props)
                )
            elif type == 'Polygon':
                polygons = [self._find_line_points(line) for line in geo]
                new_features['polygons'].append((type, polygons, props))

        data = {
            'type': 'FeatureCollection',
            'bbox': data.get('bbox', []),
            'properties': data.get('properties', {}),
            'features': [],
        }

        print('Polygons')
        for type, feature, props in new_features['polygons']:
            print(props['id'])
            geometry = []

            for line in feature:
                geometry.append(
                    [self.points[point][0] for point in line]
                )
            data['features'].append(
                self._create_feature(type, geometry, props)
            )

        print('Lines')
        for type, feature, props in new_features['lines']:
            print([props['from'], props['to']])
            geometry = [self.points[point][0] for point in feature]
            data['features'].append(
                self._create_feature(type, geometry, props)
            )

        print('Points')
        for type, feature, props in new_features['points']:
            print(props['id'])
            geometry = self.points[feature][0]
            data['features'].append(
                self._create_feature(type, geometry, props)
            )

        with open(output, 'w+') as output_file:
            output_file.write(json.dumps(data, indent=4))

    def _create_feature(self, type, geo, props):
        return {
            'type': 'Feature',
            'geometry': {
                'type': type,
                'coordinates': geo,
            },
            'properties': props,
        }

    def _find_line_points(self, line):
        return [self._find(point) for point in line]

    def _find(self, point):
        for idx, (p, points_list) in enumerate(self.points):
            if (
                math.fabs(float(p[0]) - float(point[0])) +
                math.fabs(float(p[1]) - float(point[1])) < self.tolerance
            ):
                points_list.append(p)
                return idx
        self.points.append((point, [point]))
        return len(self.points) - 1


class Split(Command):
    option_list = (
        Option('--source', '-s', dest='source'),
        Option('--output', '-o', dest='output')
    )

    def run(self, source, output, db=None):
        with open(source) as data_file:
            data = json.loads(data_file.read())

        features = data['features']

        with open(os.path.join(output, 'cities.geo.json'), 'w+') as file:
            file.write(json.dumps({
                'type': 'FeatureCollection',
                'features': [
                    f for f in features if f['geometry']['type'] == 'Point'
                ],
            }))

        with open(os.path.join(output, 'junctions.geo.json'), 'w+') as file:
            file.write(json.dumps({
                'type': 'FeatureCollection',
                'features': [
                    f for f in features
                    if f['geometry']['type'] == 'LineString'
                ],
            }))

        with open(os.path.join(output, 'areas.geo.json'), 'w+') as file:
            file.write(json.dumps({
                'type': 'FeatureCollection',
                'features': [
                    f for f in features if f['geometry']['type'] == 'Polygon'
                ],
            }))


class Build(Command):
    option_list = (
        Option('--name', '-n', dest='name'),
        Option('--path', '-p', dest='path'),
        Option('--geo', '-g', dest='geo'),
        Option('--output', '-o', dest='output'),
    )

    def run(self, name, path, geo, output, db=None):
        current_dir = os.getcwd()
        folder = ''
        if name:
            folder = os.path.join(current_dir, 'config/data/{0}'.format(name))
        if path:
            folder = os.path.join(current_dir, path)

        map_data = load(open(folder+'/map.yaml', 'r'))

        with open(geo) as data_file:
            data = json.loads(data_file.read())

        result = {
            'type': 'FeatureCollection',
            'bbox': data.get('bbox', []),
            'properties': data.get('properties', {}),
            'features': [],
        }

        for feature in data['features']:
            type = feature['properties']['type']
            if type == 'CITY':
                id = feature['properties']['id']
                city_data = next(
                    city for city in map_data['cities'] if city['name'] == id
                )
                result['features'].append(self._create_feature(
                    feature['geometry'], {
                        'type': type,
                        'id': id,
                        'area': city_data['area'],
                        'slots': city_data['slots'],
                    }
                ))
            elif type == 'AREA':
                id = feature['properties']['id']
                area_data = next(
                    area for area in map_data['areas'] if area['name'] == id
                )
                print(id, area_data)
                result['features'].append(self._create_feature(
                    feature['geometry'], {
                        'type': type,
                        'id': id,
                        'color': area_data['color'],
                    }
                ))
            elif type == 'JUNCTION':
                to_city = feature['properties']['to']
                from_city = feature['properties']['from']
                junction_data = next(
                    junction for junction in map_data['junctions']
                    if to_city in junction['between'] and
                    from_city in junction['between']
                )
                result['features'].append(self._create_feature(
                    feature['geometry'], {
                        'type': type,
                        'id': '{}_{}'.format(to_city, from_city),
                        'between': junction_data['between'],
                    }
                ))

        with open(output, 'w+') as output_file:
            output_file.write(json.dumps(result, indent=4))

        # app.logger.info('Finished building')

    def _create_feature(self, geometry, props):
        return {
            'type': 'Feature',
            'geometry': geometry,
            'properties': props,
        }


class GenerateMapData(Command):
    option_list = (
        Option('--name', '-n', dest='name'),
        Option('--path', '-p', dest='path'),
        Option('--output', '-o', dest='output'),
    )

    def run(self, name, path, output, db=None):
        current_dir = os.getcwd()
        folder = ''
        if name:
            folder = os.path.join(current_dir, 'config/data/{0}'.format(name))
        if path:
            folder = os.path.join(current_dir, path)

        common_data = load(open(folder+'/common.yaml', 'r'))
        map_data = load(open(folder+'/map.yaml', 'r'))
        stations_data = load(open(folder+'/stations.yaml', 'r'))
        steps_data = load(open(folder+'/steps.yaml', 'r'))

        result = {}

        result.update(common_data)
        result.update(stations_data)
        result.update(steps_data)
        result.update(map_data)

        exclude_fields = [
            'visibleStationsCount', 'resourceInitials', 'activeStationsCount',
            'auction', 'initialStationRules'
        ]
        for exclude_field in exclude_fields:
            result.pop(exclude_field, None)

        with open(output, 'w+') as output_file:
            output_file.write(json.dumps(result, indent=4))
