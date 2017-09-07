# energynet-server

#### How to setup dev environment:
[Setup dev environment](docs/setup.md)


#### How to generate field:
[Generate field](docs/generate_field.md)

#### How to run server:
```ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=app.py flask run```

#### How to run tests:
```ENERGYNET_CONFIG=etc/config_tests.ini nose2```

#### How to run tests with coverage:
```ENERGYNET_CONFIG=etc/config_tests.ini nose2  --with-coverage --coverage-report html```  
and look at `/htmlcov/index.html`

#### How to get list of commands:
```ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=manage.py python manage.py -?```
