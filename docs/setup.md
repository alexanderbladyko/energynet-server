# Setup dev environment

* configure python 3.6 virtual environment
```
which python3.6
mkvirtualenv nrg --python=<path to python3.6>
```

* Install requirements
```
make requirements
```

* Install dev requirements
```
make dev_requirements
```

* Setup dev environment
```
make environment_up
```

* Add nginx config in /etc/nginx/sites-enabled/default

```
server {
  listen 80;
  server_name energynet.com;
  access_log /var/log/nginx/energynet.log;

  location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_redirect off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  location ~ /(auth/.*|game_api/.*|config)$ {
    proxy_pass http://127.0.0.1:5000;
    proxy_redirect off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  location /socket.io {
    proxy_pass http://127.0.0.1:5000/socket.io;
    proxy_redirect off;
    proxy_buffering off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
  }


  location /browser-sync/socket.io/ {
    proxy_pass http://127.0.0.1:3000;
    proxy_redirect off;
    proxy_buffering off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";

  }

  location /__webpack_hmr {
    proxy_pass http://127.0.0.1:3000;
    proxy_redirect off;
    proxy_buffering off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
  }

}
```

* To run migrations
```
FLASK_APP=app.py python manage.py sync_db
```
