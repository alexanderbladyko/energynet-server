FROM python:3.6.0

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY config.ini .

RUN pwd
RUN ls

COPY entrypoint.sh .
CMD ["/usr/src/app/entrypoint.sh"]
