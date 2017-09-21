# energynet-server

#### How to setup dev environment:
[Setup dev environment](docs/setup.md)


#### How to generate field:
[Generate field](docs/generate_field.md)

#### How to run server:
```FLASK_APP=app.py flask run```

#### How to run tests:
before running
```TEST=true FLASK_APP=manage.py python manage.py sync_db```
run tests
```make test```

#### How to run tests with coverage:
```make test_coverage```  
and look at `/htmlcov/index.html`

#### How to get list of commands:
```FLASK_APP=manage.py python manage.py -?```
