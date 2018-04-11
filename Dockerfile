FROM python:3

WORKDIR /usr/src/octosearch

RUN apt-get update && apt-get install -y nginx supervisor build-essential libpoppler-cpp-dev pkg-config libldap2-dev libsasl2-dev cifs-utils && rm -rf /var/lib/apt/lists/*

COPY Pipfile .
COPY Pipfile.lock .
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install --no-cache-dir pipenv uwsgi && pipenv install

COPY . .
COPY util/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80/tcp

RUN ln -sf /dev/stdout /var/log/nginx/access.log && echo "daemon off; error_log /dev/stdout info;" >> /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default
COPY util/nginx.conf /etc/nginx/sites-enabled/default

CMD [ "util/docker-startup.sh" ]
