FROM python:3.11.0b5-alpine3.16
ARG appdir=/usr/src/app
WORKDIR $appdir

RUN export DB_HOST=DB_HOST
RUN export	DB_DATABASE=DB_DATABASE
RUN export DB_PORT=3306
RUN export DB_USERNAME=DB_USERNAME
RUN export DB_PASSWORD=DB_PASSWORD

RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev  bash
RUN apk add mysql-client
RUN apk add build-base

ADD requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
#COPY .env .env

COPY migration migration
RUN dos2unix migration/migration.sh
RUN dos2unix migration/migration.txt
RUN chmod 701  migration/migration.sh
# RUN migration/migration.sh $appdir/migration > /tmp/migration.txt

COPY src src
COPY prodfiles/run.sh run.sh
RUN dos2unix run.sh
RUN chmod 701 run.sh
COPY prodfiles/crontab /etc/cron.d/my-crontab
RUN dos2unix /etc/cron.d/my-crontab
RUN chmod 0644 /etc/cron.d/my-crontab && crontab /etc/cron.d/my-crontab


CMD ["bash", "run.sh"]
# CMD ["bash", "-c", "/usr/sbin/crond -f ; python /usr/src/app/src/web.py"]
