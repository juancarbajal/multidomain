FROM python:3.11.0b5-alpine3.16
EXPOSE 5000
WORKDIR /usr/src/app

RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev
RUN apk add build-base
ADD requirements_web.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements_web.txt
COPY .env .env
COPY src src

CMD ["python", "/usr/src/app/src/web.py"]
