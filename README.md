Ducky
=====

Requirements
------------

 * pipenv
 * flask
 * python-ldap

mountedcifs:

 * getcifsacls

Development
-----------

To start the web interface: 

    $ pipenv run ./ducky.py --webserver indexname

An elastic search server can be started with docker.
For a first time, run:

    $ docker run -i --name elasticsearch -v esdata:/usr/share/elasticsearch/data  docker.elastic.co/elasticsearch/elasticsearch-oss:6.0.1

After that:

    $ docker start elasticsearch

Troubleshooting
---------------

In case you get a systemd error with docker about a cpu.shares file not found:

 * https://stackoverflow.com/questions/32845917/docker-cannot-start-container-cpu-shares-no-such-file-or-directory#32878801

Or an error about vm_map_max:

    $ sudo sysctl -w vm.max_map_count=262144

 * https://github.com/docker-library/elasticsearch/issues/111
