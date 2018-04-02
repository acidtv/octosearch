#FROM python:3
FROM octo-test1

WORKDIR /usr/src/octosearch

COPY . .
#RUN apt-get update
#RUN apt-get install -y build-essential libpoppler-cpp-dev pkg-config libldap2-dev libsasl2-dev cifs-utils
#RUN apt-get install -y nginx supervisor
#RUN pip install --no-cache-dir pipenv uwsgi
RUN export PIPENV_VENV_IN_PROJECT=1 && pipenv install

COPY util/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

#RUN rm -rf /var/lib/apt/lists/*

#EXPOSE 5000/tcp

# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# Remove default configuration from Nginx
RUN rm -f /etc/nginx/conf.d/default.conf
# Copy the modified Nginx conf
COPY util/nginx.conf /etc/nginx/conf.d/

CMD [ "util/docker-startup.sh" ]
