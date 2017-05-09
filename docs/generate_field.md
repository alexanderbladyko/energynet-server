## Generating geojson


#### to normalize
```
ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=manage.py python manage.py config.normalize -s config/data/russia/source/geo.json -o config/data/russia/normalized/geo.json -t 1
```

#### to split
```
ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=manage.py python manage.py config.geo.split -s config/data/russia/source/geo.json -o config/data/russia/
```

#### to build
```
ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=manage.py python manage.py config.build -n russia -g config/data/russia/normalized/geo.json --output config/data/russia/generated/geo.json
```

#### to build map data
```
ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=manage.py python manage.py config.generate.map_data -n russia --output config/data/russia/generated/map_data.json
```
