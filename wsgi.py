#!/usr/bin/env python

from octosearch import web

# make elasticsearch module available to web package
from octosearch.backends import elasticsearch

application = web.app

if __name__ == '__main__':
    application.run()
