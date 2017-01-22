> configure python 3 virtual environment  

> Install requirements

```
pip install -r etc/requirements.txt
```

> copy config.ini into config_local.ini
> making [app] debug=True is highely recommended  

> Add nginx config in /etc/nginx/sites-enabled/default

```
server {
  listen 80;
  server_name localhost;
  access_log /var/log/nginx/example.log;

  location ~ /(game_api/.*|config)$ {
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
}
```

> To run migrations
```
ENERGYNET_CONFIG=etc/config_local.ini FLASK_APP=app.py python manage.py sync_db
```

> To run tests use
```
python -m unittest discover
```
