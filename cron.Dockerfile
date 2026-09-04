FROM python:3.11.0b5-alpine3.16
WORKDIR /usr/src/app

RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev  
RUN apk add build-base
ADD requirements_cron.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements_cron.txt
COPY .env .env
COPY src src
COPY crontab /etc/cron.d/my-crontab
RUN chmod 0644 /etc/cron.d/my-crontab && crontab /etc/cron.d/my-crontab

CMD ["/usr/sbin/crond", "-f"]

