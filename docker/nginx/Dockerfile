FROM nginx:1.11.5-alpine

EXPOSE 80 443

RUN mkdir /logs
COPY nginx.conf /etc/nginx/
COPY energynet.conf /etc/nginx/sites-enabled/
