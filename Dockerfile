FROM python:3
#FROM octo-test1

WORKDIR /usr/src/octosearch

RUN apt-get update && apt-get install -y nginx supervisor build-essential libpoppler-cpp-dev pkg-config libldap2-dev libsasl2-dev cifs-utils && rm -rf /var/lib/apt/lists/*

COPY Pipfile .
COPY Pipfile.lock .
RUN pip install --no-cache-dir pipenv uwsgi && export PIPENV_VENV_IN_PROJECT=1 && pipenv install

COPY . .
COPY util/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80/tcp

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/conf.d/default.conf
COPY util/nginx.conf /etc/nginx/conf.d/

CMD [ "util/docker-startup.sh" ]
