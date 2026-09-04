FROM python:3.6-slim

WORKDIR /srv/flask_app

COPY src .
COPY uwsgi.ini .
COPY nginx.conf /etc/nginx
COPY start.sh .

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
		&& apt-get -y install build-essential

ADD requirements_web.txt .
RUN pip install -r requirements_web.txt --src /usr/local/src

RUN chmod +x ./start.sh
CMD ["bash", "./start.sh"]
