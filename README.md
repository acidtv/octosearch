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

 $ export FLASK_APP=web/webserver.py && export FLASK_DEBUG=1 && pipenv run flask run

