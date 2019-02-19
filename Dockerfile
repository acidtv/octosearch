FROM python:3

WORKDIR /usr/src/octosearch

# install deps with apt
RUN apt-get update && apt-get install -y nginx supervisor build-essential \
    libpoppler-cpp-dev pkg-config libldap2-dev libsasl2-dev cifs-utils \
    libsmbclient-dev libsmbclient less \
    && rm -rf /var/lib/apt/lists/*

# install requirements
COPY requirements.txt .
RUN pip install uwsgi && pip install -r requirements.txt

# set up app
COPY . .

# install app in dev mode
RUN pip3 install -e .

# set up supervisord for uswsgi and nginx
COPY util/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# set up nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN rm -f /etc/nginx/sites-enabled/default
COPY util/nginx.conf /etc/nginx/sites-enabled/default

EXPOSE 80/tcp

CMD [ "util/docker-startup.sh" ]
