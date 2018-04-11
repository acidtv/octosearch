Octosearch
==========

Octosearch is search server. It indexes your local and remote filesystems, internal websites and cloud storage so you can easily find what you're looking for.

Requirements
------------

 The project runs on Python 3, most systems will have that installed already. 
 Python dependencies are managed with pipenv, so you'll need that.

### Installing dependencies

Installation
-----------

This project is not published on pip yet, so we'll have to jump through some hoops to get it working. If you're the lazy kind of person (like me) you might want to skip the manual install instructions  and try a Docker image instead. 

### Manual installation

First, clone the source code from github.

This would be a good time to install some dependencies:

    $ sudo apt-get install build-essential libpoppler-cpp-dev pkg-config python-dev libldap2-dev libsasl2-dev cifs-utils
    $ pipenv install

The project needs to be installed in 'development mode' with setuptools. This is necessary for any internal and external plugins to work:

    $ python3 setup.py develop

Octosearch uses Elasticsearch for indexing documents. If you want to install Elasticsearch manually, have a look here: https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html#install-elasticsearch

Alternatively, start a docker container with Elasticsearch:

    $ docker run -i --name elasticsearch -v esdata:/usr/share/elasticsearch/data  docker.elastic.co/elasticsearch/elasticsearch-oss:6.0.1

Now you can start the Octosearch web interface in development mode: 

    $ pipenv run ./octosearch.py --webserver

If you're going to use Octosearch in production it's a good idea to run it behind a webserver, like nginx for example. To do that install uwsgi, and configure nginx to connect to uwsgi.

This is by no means a comprehensive guide to running Octosearch in production, just some pointers to get you started.

Uwsgi should be aware of the virtualenv you're using. Your uwsgi command should look something like this:

    $ /usr/local/bin/uwsgi --virtualenv=/usr/src/octosearch/.venv -s /tmp/octosearch.sock --wsgi-file wsgi.py --uid www-data --gid www-data

Then tell nginx where to find uwsgi:

    server {
    	listen 80;

    	location / {
    		include uwsgi_params;
    		uwsgi_pass unix:///tmp/octosearch.sock;
    	}
    }

### Using Docker

Octosearch is not published on Docker hub yet, but you can easily build your own image.

To build an image use:

    $ docker-compose build 

You will also need Elasticsearch. To run your image and connect it to Elasticsearch you can use the included docker-compose.yml:

    $ docker-compose up

Troubleshooting
---------------

### The search doesn't work 

This project is still in the early stages of it's development, so the elasticsearch field mappings change from time to time. Try truncating and re-indexing.

    $ pipenv run ./octosearch.py --truncate && pipenv run ./octosearch.py --index

### In case you get a systemd error with docker about a cpu.shares file not found

 * https://stackoverflow.com/questions/32845917/docker-cannot-start-container-cpu-shares-no-such-file-or-directory#32878801

### An error about vm_map_max

    $ sudo sysctl -w vm.max_map_count=262144

 * https://github.com/docker-library/elasticsearch/issues/111
